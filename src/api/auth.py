from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.services.auth import create_user, authenticate_user, get_user_by_id
from src.core.security import require_auth, set_user_session, clear_user_session

router = APIRouter(prefix="/api/auth", tags=["认证"])

class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    success: bool
    user: UserResponse | None = None
    message: str | None = None

@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次密码不一致"
        )
    
    user = create_user(db, request.username, request.password)
    
    return AuthResponse(
        success=True,
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    fastapi_request: Request,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    set_user_session(fastapi_request, user.id)
    
    return AuthResponse(
        success=True,
        user=UserResponse.model_validate(user)
    )

@router.post("/logout", response_model=AuthResponse)
async def logout(
    fastapi_request: Request,
    user_id: int = Depends(require_auth)
):
    clear_user_session(fastapi_request)
    
    return AuthResponse(
        success=True,
        message="已登出"
    )

@router.get("/me", response_model=AuthResponse)
async def get_current_user(
    user_id: int = Depends(require_auth),
    db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return AuthResponse(
        success=True,
        user=UserResponse.model_validate(user)
    )
