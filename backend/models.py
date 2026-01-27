from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class User(Base):
    """
    用户数据库模型
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False) # 用户名
    password = Column(String, nullable=False) # 密码 (哈希值)
    nickname = Column(String) # 昵称
    phone = Column(String) # 手机号
    email = Column(String) # 邮箱
    gender = Column(String) # 性别: '男' 或 '女'
    role = Column(String, default="user") # 角色: 'admin' 或 'user'

class Audio(Base):
    """
    音频记录数据库模型
    """
    __tablename__ = "audios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False) # 关联的用户ID
    audio_path = Column(Text, nullable=False) # 音频文件存储路径
    emo_type = Column(Integer, default=0) # 情感类型: 0:喜, 1:怒, 2:哀, 3:惧 
    create_time = Column(DateTime, default=datetime.now) # 创建时间
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now) # 更新时间
