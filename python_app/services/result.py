from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from python_app.models import Event, Winner, User, LotteryHistory

async def get_event_results(event_id: int, db: AsyncSession):
    query = (
        select(Event, LotteryHistory)
        .join(LotteryHistory, Event.id == LotteryHistory.event_id)
        .where(Event.id == event_id)
    )
    result = await db.execute(query)
    data = result.first()

    if not data:
        return None

    event, history = data

    winner_query = (
        select(User.id, User.nickname, User.email)
        .join(Winner, User.id == Winner.user_id)
        .where(Winner.event_id == event_id)
    )
    winner_result = await db.execute(winner_query)
    winners_data = winner_result.all()

    if history.winner_count > 0:
        rate = f"{history.total_applicants / history.winner_count:.1f} : 1"
    else:
        rate = "0 : 1"

    return {
        "event_id": event.id,
        "event_title": event.title,
        "draw_info": {
            "total_applicants": history.total_applicants,
            "winner_count": history.winner_count,
            "competition_rate": rate
        },
        "winners": [
            {
                "user_id": w.id,
                "nickname": w.nickname,
                "email": w.email
            } for w in winners_data
        ]
    }