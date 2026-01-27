from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database, auth

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """
    获取当前登录用户的个人信息。
    """
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_user_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(database.get_db)):
    """
    更新当前登录用户的个人信息。
    """
    # 更新允许的字段
    current_user.nickname = user_update.nickname
    current_user.phone = user_update.phone
    current_user.email = user_update.email
    current_user.gender = user_update.gender
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/password")
async def update_password_me(old_password: str, new_password: str, current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(database.get_db)):
    """
    修改当前登录用户的密码。
    """
    if not auth.verify_password(old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    current_user.password = auth.get_password_hash(new_password)
    db.commit()
    return {"message": "Password updated successfully"}

# 管理员路由
@router.get("/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    管理员接口：获取所有用户列表。
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    管理员接口：删除指定用户。
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@router.post("/{user_id}/reset_password")
async def reset_password(user_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # 重置为 123456
    user.password = auth.get_password_hash("123456")
    db.commit()
    return {"message": "Password reset to 123456"}

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    管理员接口：更新指定用户的信息。
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.nickname = user_update.nickname
    db_user.phone = user_update.phone
    db_user.email = user_update.email
    db_user.gender = user_update.gender
    # 管理员也可以更新角色（如果我们将其添加到 schema 中），但目前 UserUpdate schema 没有角色字段。
    # 我们暂时只更新基本信息。
    
    db.commit()
    db.refresh(db_user)
    return db_user
