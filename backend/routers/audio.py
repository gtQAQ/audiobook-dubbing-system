from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database, auth, tts_service
from config import DATA_DIR, OUTPUT_DIR, PROJECT_ROOT, TEMP_DIR
import shutil, os

router = APIRouter(prefix="/audio", tags=["Audio"])

def resolve_output_path_to_abs_path(path_or_url: str) -> str:
    """
    将音频路径统一解析为磁盘绝对路径。
    
    说明：
    - 推荐输入：以 /output/... 开头的 URL 路径（后端返回/数据库存储的标准格式）。
    - 兼容输入：允许字符串中包含 /output/... 片段，以及旧版 ../output/... 
    - 该函数仅负责“解析”，不负责鉴权与目录边界校验；调用方需自行做白名单目录校验。
    """
    if not path_or_url:
        # 空值直接返回空字符串，便于上层做统一错误处理
        return ""

    # 统一路径分隔符，避免 Windows 反斜杠导致解析逻辑失效
    candidate = path_or_url.replace("\\", "/").strip()

    if candidate.startswith("/output/"):
        # 标准情况：前端/数据库存的是 /output/... 形式的 URL 路径
        relative = candidate[len("/output/"):].lstrip("/")
        return os.path.abspath(os.path.join(OUTPUT_DIR, *relative.split("/")))

    output_index = candidate.find("/output/")
    if output_index != -1:
        # 兼容情况：字符串中包含 /output/... 片段
        relative = candidate[output_index + 1 :].lstrip("/")
        return os.path.abspath(os.path.join(PROJECT_ROOT, *relative.split("/")))

    candidate = candidate.lstrip("./")
    if candidate.startswith("../"):
        # 兼容情况：../output/... 这种基于项目根目录的相对路径
        return os.path.abspath(os.path.join(PROJECT_ROOT, *candidate.lstrip("./").split("/")))

    # 兜底：当作相对项目根目录的路径处理
    return os.path.abspath(os.path.join(PROJECT_ROOT, *candidate.split("/")))

@router.post("/upload_text")
async def upload_text(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    上传文本文件并读取其内容。
    支持 .txt 格式，自动尝试 UTF-8 和 GBK 编码解码。
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="仅支持 .txt 文件")
    
    content = await file.read()
    # 优先按 utf-8 解码，失败则回退到 gbk
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = content.decode("gbk")
        except:
            raise HTTPException(status_code=400, detail="文件解码失败")
            
    return {"filename": file.filename, "content": text}

@router.post("/synthesize")
async def synthesize(text: str = Form(...), emo_type: int = Form(...), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    接收文本和情感类型，调用 TTS 服务生成音频。
    """
    # 调用 TTS 服务
    audio_path = tts_service.synthesize_audio(text, emo_type)
    if not audio_path:
        raise HTTPException(status_code=500, detail="语音合成服务失败")
    
    return {"audio_path": audio_path}

@router.post("/save", response_model=schemas.Audio)
async def save_audio(emo_type: int = Form(...), audio_path: str = Form(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    将生成的临时音频文件保存到持久化存储目录，并在数据库中创建记录。
    """
    # 将前端传入的音频路径解析为磁盘绝对路径，确保后端能定位到实际文件
    src_abs_path = resolve_output_path_to_abs_path(audio_path)
    
    if not os.path.exists(src_abs_path):
         raise HTTPException(status_code=404, detail="音频文件未找到")

    temp_dir_abs = os.path.abspath(TEMP_DIR)
    if os.path.commonpath([src_abs_path, temp_dir_abs]) != temp_dir_abs:
        # 限制只能保存临时目录下的音频，避免路径穿越导致任意文件被复制到公开目录
        raise HTTPException(status_code=400, detail="非法的音频路径")
    
    # 2. 定义目标路径 (数据文件)
    filename = os.path.basename(src_abs_path)
    dst_abs_path = os.path.join(DATA_DIR, filename)
    
    # 3. 复制文件
    try:
        shutil.copy(src_abs_path, dst_abs_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存音频文件失败: {e}")
        
    db_audio = models.Audio(
        user_id=current_user.id,
        audio_path=f"/output/data/{filename}",
        emo_type=emo_type
    )
    db.add(db_audio)
    db.commit()
    db.refresh(db_audio)
    return db_audio

@router.get("/", response_model=List[schemas.Audio])
async def list_audios(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # 显示用户自己的音频
    audios = db.query(models.Audio).filter(models.Audio.user_id == current_user.id).order_by(models.Audio.create_time.desc()).all()
    return audios

@router.delete("/{audio_id}")
async def delete_audio(audio_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    根据 ID 删除指定的音频记录。
    如果文件存在，也会尝试从磁盘删除。仅限所有者或管理员操作。
    """
    audio = db.query(models.Audio).filter(models.Audio.id == audio_id).first()
    if not audio:
        raise HTTPException(status_code=404, detail="音频记录不存在")
    if audio.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    audio_abs_path = resolve_output_path_to_abs_path(audio.audio_path)
    output_dir_abs = os.path.abspath(OUTPUT_DIR)
    if (
        audio_abs_path
        and os.path.commonpath([audio_abs_path, output_dir_abs]) == output_dir_abs
        and os.path.exists(audio_abs_path)
    ):
        try:
            os.remove(audio_abs_path)
        except Exception:
            pass
            
    db.delete(audio)
    db.commit()
    return {"message": "音频已删除"}
