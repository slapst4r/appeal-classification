from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Appeal
from app.schemas import AnalyticsResponse

async def get_analytics(db: AsyncSession) -> AnalyticsResponse:
    # Общее количество
    total_q = select(func.count(Appeal.id))
    total = (await db.execute(total_q)).scalar_one()

    # Количество обращений с ненормативной лексикой
    profanity_q = select(func.count(Appeal.id)).where(Appeal.contains_explicit == True)
    profanity_count = (await db.execute(profanity_q)).scalar_one()

    profanity_share = profanity_count / total if total > 0 else 0.0

    # Распределение по категориям
    cat_q = select(
        func.coalesce(Appeal.category, "Без категории (ненормативная лексика)"),
        func.count()).group_by(func.coalesce(Appeal.category, 'Без категории'))
    rows = (await db.execute(cat_q)).all()
    categories_distribution = {row[0]: row[1] for row in rows}

    return AnalyticsResponse(
        total_appeals=total,
        categories_distribution=categories_distribution,
        profanity_share=round(profanity_share, 4)
    )