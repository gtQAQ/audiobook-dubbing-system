from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """
    用户基础数据模型 (Pydantic)
    """
    username: str
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None

class UserCreate(UserBase):
    """
    用户创建模型 (包含密码)
    """
    password: str

class UserUpdate(UserBase):
    """
    用户更新模型
    """
    pass

class User(UserBase):
    """
    用户响应模型 (包含 ID 和角色)
    """
    id: int
    role: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    """
    Token 响应模型
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Token 数据载荷
    """
    username: Optional[str] = None

class AudioBase(BaseModel):
    """
    音频基础数据模型
    """
    emo_type: int
    text_content: Optional[str] = None

class AudioCreate(AudioBase):
    pass

class Audio(AudioBase):
    """
    音频响应模型
    """
    id: int
    user_id: int
    audio_path: str
    create_time: datetime
    class Config:
        orm_mode = True
