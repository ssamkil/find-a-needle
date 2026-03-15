from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from python_app.db.session import get_db
from python_app.models import User, Winner, LotteryHistory
from python_app.schemas import WinnerResponse, LotteryHistoryResponse, LotteryResultResponse, AdminLotteryResultResponse
from python_app.api import dependencies
from python_app.services import get_event_results

router = APIRouter()

@router.get("/me", response_model=List[WinnerResponse])
async def get_my_wins(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(dependencies.get_current_user)
):
    result = await db.execute(
        select(Winner).where(Winner.user_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/event/{event_id}", response_model=List[WinnerResponse])
async def get_event_winners(
        event_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Winner)
        .options(joinedload(Winner.user))
        .where(Winner.event_id == event_id)
    )
    winners = result.scalars().all()

    return winners

@router.get("/event/{event_id}/history", response_model=LotteryHistoryResponse)
async def get_event_lottery_history(
        event_id: int,
        db: AsyncSession = Depends(get_db),
        current_admin: User = Depends(dependencies.get_current_admin)
):
    result = await db.execute(
        select(LotteryHistory).where(LotteryHistory.event_id == event_id)
    )
    history = result.scalar_one_or_none()

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 이벤트의 추첨 기록이 없습니다."
        )

    return history

@router.get("/{event_id}/results", response_model=LotteryResultResponse)
async def get_public_lottery_results(
        event_id: int,
        db: AsyncSession = Depends(get_db)
):
    results = await get_event_results(event_id, db)

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="결과가 아직 준비되지 않았습니다."
        )

    return results

@router.get("/{event_id}/admin/results", response_model=AdminLotteryResultResponse)
async def fetch_admin_lottery_results(
        event_id: int,
        db: AsyncSession = Depends(get_db),
        current_admin: User = Depends(dependencies.get_current_admin)
):
    results = await get_event_results(event_id, db)

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="추첨 결과가 존재하지 않거나 잘못된 이벤트 ID입니다."
        )

    return results