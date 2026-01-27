import os

# 定义后端的基准目录 (d:\Audiobook Dubbing System\backend)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# 为了向后兼容导入 BASE_DIR 的模块
BASE_DIR = BACKEND_DIR

# 定义项目的根目录 (d:\Audiobook Dubbing System)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

# 定义相对于项目根目录的其他路径
VOICE_DIR = os.path.join(PROJECT_ROOT, "voice")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")

# 数据库路径 (保留在 backend 目录还是根目录？目前既然移动了就保留在 backend 目录)
DATABASE_PATH = os.path.join(BACKEND_DIR, "sql_app.db")

# 前端构建输出路径
FRONTEND_DIST_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")
