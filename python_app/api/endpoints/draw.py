from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from python_app.db.session import get_db
from python_app.models import User
from python_app.api import dependencies
from python_app.services.auto_draw import perform_draw

router = APIRouter()

@router.post("/{event_id}")
async def perform_draw_manual(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(dependencies.get_current_admin)
):
    try:
        result = await perform_draw(event_id, db, current_admin.id)

        await db.commit()

        return {"message": "수동 추첨 완료", **result}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )