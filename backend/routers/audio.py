from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas, database, auth, tts_service
from config import BASE_DIR, DATA_DIR
import shutil, os, uuid

router = APIRouter(prefix="/audio", tags=["Audio"])

@router.post("/upload_text")
async def upload_text(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    上传文本文件并读取其内容。
    支持 .txt 格式，自动尝试 UTF-8 和 GBK 编码解码。
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")
    
    content = await file.read()
    # 假设是 utf-8 
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = content.decode("gbk")
        except:
            raise HTTPException(status_code=400, detail="Could not decode file")
            
    return {"filename": file.filename, "content": text}

@router.post("/synthesize")
async def synthesize(text: str = Form(...), emo_type: int = Form(...), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    接收文本和情感类型，调用 TTS 服务生成音频。
    """
    # 调用 TTS 服务
    audio_path = tts_service.synthesize_audio(text, emo_type)
    if not audio_path:
        raise HTTPException(status_code=500, detail="TTS synthesis failed")
    
    return {"audio_path": audio_path}

@router.post("/save", response_model=schemas.Audio)
async def save_audio(emo_type: int = Form(...), audio_path: str = Form(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    将生成的临时音频文件保存到持久化存储目录，并在数据库中创建记录。
    """
    # 1. 解析源路径 (临时文件)
    # 前端传来的 audio_path 是相对路径，例如 "..\output\temp\xxx.wav" 或 "output\temp\xxx.wav"
    # 我们需要将其转换为绝对路径才能找到它。
    
    # 尝试先相对于 BASE_DIR 解析
    src_abs_path = os.path.abspath(os.path.join(BASE_DIR, audio_path))
    
    if not os.path.exists(src_abs_path):
         raise HTTPException(status_code=404, detail="Audio file not found")
    
    # 2. 定义目标路径 (数据文件)
    filename = os.path.basename(src_abs_path)
    dst_abs_path = os.path.join(DATA_DIR, filename)
    
    # 3. 复制文件
    try:
        shutil.copy(src_abs_path, dst_abs_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save audio file: {e}")
        
    # 4. 为数据库生成新的相对路径
    new_rel_path = os.path.relpath(dst_abs_path, BASE_DIR).replace("\\", "/")

    db_audio = models.Audio(
        user_id=current_user.id,
        audio_path=new_rel_path,
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
        raise HTTPException(status_code=404, detail="Audio not found")
    if audio.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # 删除文件 (如果存在)
    if os.path.exists(audio.audio_path):
        try:
            os.remove(audio.audio_path)
        except:
            pass
            
    db.delete(audio)
    db.commit()
    return {"message": "Audio deleted"}
