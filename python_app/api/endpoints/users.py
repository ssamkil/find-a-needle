from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from python_app.db.session import get_db
from python_app.models import User
from python_app.schemas import UserCreate, UserResponse
from python_app.core import get_password_hash
from python_app.api import dependencies

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        *,
        db: AsyncSession = Depends(get_db),
        user_in: UserCreate
) -> Any:
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=400,
            detail="이미 존재하는 이메일입니다."
        )

    db_user = User(
        email=user_in.email,
        nickname=user_in.nickname,
        password_hash=get_password_hash(user_in.password),
        is_active=True
    )

    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="유저 저장 중 오류가 발생했습니다."
        )

    return db_user

@router.get("/me", response_model=UserResponse)
async def read_user_me(
        current_user: User = Depends(dependencies.get_current_user)
) -> Any:
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(dependencies.get_current_user)
) -> Any:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유저를 찾을 수 없습니다."
        )

    return user