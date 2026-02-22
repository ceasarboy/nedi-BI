from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.security import require_auth, get_current_user_id
from src.services.auth import get_user_by_id, can_access_resource, is_admin

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = require_auth(request)
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

def check_resource_access(
    user,
    resource_user_id: int | None,
    resource_name: str = "资源"
):
    if not can_access_resource(user, resource_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"无权访问此{resource_name}"
        )

def get_current_user_and_check(
    request: Request,
    db: Session = Depends(get_db),
    resource_user_id: int | None = None,
    resource_name: str = "资源"
):
    user = get_current_user(request, db)
    if resource_user_id is not None:
        check_resource_access(user, resource_user_id, resource_name)
    return user

def filter_by_user_permission(query, user, user_id_field):
    if is_admin(user):
        return query
    return query.filter(user_id_field == user.id)
