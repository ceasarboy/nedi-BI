import bcrypt
from fastapi import Request, HTTPException, status

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def get_current_user_id(request: Request) -> int | None:
    return request.session.get('user_id')

def require_auth(request: Request) -> int:
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录"
        )
    return user_id

def set_user_session(request: Request, user_id: int):
    request.session['user_id'] = user_id

def clear_user_session(request: Request):
    request.session.pop('user_id', None)
