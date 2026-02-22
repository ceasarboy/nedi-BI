from sqlalchemy.orm import Session
from src.models.user import User
from src.core.security import hash_password, verify_password
from fastapi import HTTPException, status

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, username: str, password: str) -> User:
    if get_user_by_username(db, username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码至少需要6位"
        )
    
    user = User(
        username=username,
        password_hash=hash_password(password),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_admin_user(db: Session):
    admin = get_user_by_username(db, "admin")
    if not admin:
        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Admin user created: username=admin, password=admin123")
    return admin

def is_admin(user: User) -> bool:
    return user.role == "admin"

def can_access_resource(user: User, resource_user_id: int | None) -> bool:
    if is_admin(user):
        return True
    if resource_user_id is None:
        return True
    return user.id == resource_user_id
