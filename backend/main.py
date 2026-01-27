from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base
from routers import auth, users, audio
import os
from config import OUTPUT_DIR, VOICE_DIR, FRONTEND_DIST_DIR, TEMP_DIR, DATA_DIR

# 创建必要的目录
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(VOICE_DIR):
    os.makedirs(VOICE_DIR)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# 挂载输出目录 (用于访问生成的音频文件)
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")
app.mount("/voice", StaticFiles(directory=VOICE_DIR), name="voice")

# 挂载前端静态资源
if os.path.exists(os.path.join(FRONTEND_DIST_DIR, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST_DIR, "assets")), name="assets")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(audio.router)

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    提供单页应用 (SPA) 的静态文件服务。
    如果路径对应的文件存在，则返回该文件；否则返回 index.html 以支持前端路由。
    """
    # 检查 dist 中是否存在文件 (例如 favicon.ico)
    file_path = os.path.join(FRONTEND_DIST_DIR, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # 否则返回 index.html 以支持 SPA 路由
    return FileResponse(os.path.join(FRONTEND_DIST_DIR, "index.html"))
