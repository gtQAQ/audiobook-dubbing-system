# 有声读物配音系统 (Audiobook Dubbing System)

这是一个基于 **FastAPI** (后端) 和 **Vue 3** (前端) 开发的全栈有声读物配音系统，旨在为用户提供便捷的文本转语音服务。系统支持文本上传解析、多情感语音合成、在线试听及个人作品管理。

## 📁 目录结构

项目采用前后端分离的架构组织：

```
Audiobook Dubbing System
├─ backend/                 # 后端核心代码 (FastAPI)
│  ├─ routers/              # API 路由模块
│  │  ├─ audio.py           # 音频相关接口 (上传、合成、保存)
│  │  ├─ auth.py            # 认证相关接口 (登录、注册)
│  │  └─ users.py           # 用户管理接口
│  ├─ config.py             # 全局配置文件 (路径、密钥等)
│  ├─ database.py           # 数据库连接管理 (SQLite)
│  ├─ main.py               # 应用入口文件 (启动服务、挂载静态资源)
│  ├─ models.py             # 数据库模型定义 (ORM)
│  ├─ schemas.py            # 数据验证模型 (Pydantic)
│  ├─ tts_service.py        # 语音合成服务逻辑 (调用 IndexTTS 2)
│  └─ requirements.txt      # 后端依赖列表
│
├─ frontend/                # 前端核心代码 (Vue 3 + Vite)
│  ├─ src/
│  │  ├─ views/             # 页面组件 (Login, Upload, Synthesize, History 等)
│  │  ├─ layouts/           # 布局组件
│  │  ├─ router/            # 路由配置
│  │  └─ main.js            # 前端入口
│  ├─ dist/                 # 前端构建产物 (由 npm run build 生成)
│  └─ package.json          # 前端依赖列表
│
├─ output/                  # 音频输出目录
│  ├─ temp/                 # 临时合成文件 (试听用 WAV 文件)
│  └─ data/                 # 持久化保存文件 (用户保存后移动至此)
│
├─ input/                   # 测试用 TXT 文件
├─ voice/                   # 参考音频目录 (用于控制合成情感)
├─ docs/                    # 项目文档资料
├─ start.bat                # Windows 快速启动脚本
└─ README.md                # 项目说明文档
```

## 🛠️ 技术栈

*   **后端**: Python 3.10+, FastAPI, SQLAlchemy, SQLite, Uvicorn
*   **前端**: Vue 3, Vite, Element Plus, Axios, Vue Router
*   **AI 模型**: IndexTTS 2 

## 🚀 部署方案

### 1.TTS 服务配置

本项目依赖 IndexTTS 2 提供语音合成能力。

1.  **下载 TTS**: 下载 IndexTTS 2 整合包，下载地址: https://pan.baidu.com/s/1JwNTYdW7iCEXv3IdCFYOrA?pwd=bili
2.  **启动**: 双击根目录下的 `一键启动.bat`。
    *   脚本会自动启动 TTS 服务。
    *   自动打开默认浏览器访问 `http://127.0.0.1:7860`。

### 2. 环境配置

1.  **Python 环境**: 安装 Python 3.10 或更高版本。
2.  **Node.js 环境**: 安装 Node.js (用于构建前端，仅开发或首次部署需要)。    
3.  确认 Python 和 Node.js 环境已正确安装。

```powershell
python --version
node --version
npm --version
```

### 3. 后端配置

创建独立的 Python 虚拟环境并安装依赖。

```powershell
# 1. 创建名为 venv 的虚拟环境
python -m venv venv

# 2. 安装后端依赖
# 注意：直接调用虚拟环境下的 pip，无需显式激活环境
.\venv\Scripts\pip install -r backend\requirements.txt
```

### 4. 前端构建

进入前端目录，安装依赖并编译生成静态文件。

```powershell
# 1. 进入前端目录
cd frontend

# 2. 安装 Node.js 依赖
npm install

# 3. 构建静态资源 (构建产物将生成在 frontend/dist 目录)
npm run build

# 4. 返回项目根目录
cd ..
```

### 5. 启动服务

启动后端服务，FastAPI 会自动托管构建好的前端页面。

```powershell
# 启动服务
# --app-dir backend: 指定后端代码所在目录
# --host 0.0.0.0: 允许局域网访问
# --port 8000: 指定服务端口
.\venv\Scripts\uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000
```

### 6. 快速启动

使用批处理文件快速启动项目。

1.  **部署验证**: 确保已按照上述步骤正确安装依赖、构建前端静态资源，并成功启动过后端服务。完成首次验证后，可正常关闭服务。
2.  **启动**: 双击根目录下的 `start.bat`。
    *   脚本会自动启动 FastAPI 服务。
    *   自动打开默认浏览器访问 `http://127.0.0.1:8000`。

## 📝 功能特性

1.  **用户认证**: 完整的注册、登录流程，基于 JWT 的 Token 认证。
2.  **文本处理**: 支持 TXT 文件上传，自动解析编码。
3.  **语音合成**:
    *   支持四种情感预设：喜、怒、哀、惧。
    *   **临时试听**: 合成结果优先保存在 `output/temp`，避免产生大量垃圾文件。
    *   **永久保存**: 用户满意后点击保存，文件自动迁移至 `output/data` 并写入数据库。
4.  **文件管理**: 提供个人历史记录列表，支持在线播放、下载和删除。
5.  **权限控制**: 普通用户仅能管理自己的文件，管理员拥有更高权限。

## ⚠️ 注意事项

*   **数据备份**: 生产环境建议定期备份 `backend/sql_app.db` (数据库) 和 `output/data/` (音频文件)。
*   **临时文件清理**: `output/temp/` 目录下的文件为临时生成，建议配置定时任务定期清理。
