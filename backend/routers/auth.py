from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import auth, models, schemas, database

router = APIRouter(tags=["Authentication"])

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """
    用户登录接口。
    验证用户名密码，返回 JWT 令牌。
    """
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    用户注册接口。
    检查用户名是否已存在，创建新用户。如果是 'admin' 用户名则自动赋予管理员权限。
    """
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已被注册")
    hashed_password = auth.get_password_hash(user.password)
 
    # 如果用户名是 "admin"，则设为 "admin" 角色。
    role = "admin" if user.username == "admin" else "user"
    db_user = models.User(
        username=user.username,
        password=hashed_password,
        nickname=user.nickname,
        phone=user.phone,
        email=user.email,
        gender=user.gender,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
