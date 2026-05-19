from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload 
from app.database import get_db, engine
from app.models import Base, Appeal
from app.schemas import (
    ClassificationRequest, ClassificationResponse, AppealFromDB, AnalyticsResponse, CategoryResult
)
from app.classification.classifier import AppealClassifier
from app.analytics import get_analytics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Классификатор обращений")
classifier = AppealClassifier()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/classify", response_model=ClassificationResponse)

async def classify_appeal(
    
    req: ClassificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Главная функция для классификации обращений
    Args:
        text (string): Текст обращения

    Returns:
    {
        "id": новое id,
        "category": {
            "category": Категория
            "reason": "Причина"
        },
        "created_at": Дата создания
    }
    """
    category, contains_explicit, unclass_reason = await classifier.classify(req.text)

    appeal = Appeal(
        text=req.text,
        contains_explicit=contains_explicit,
        unclassified_reason=unclass_reason,
        category=category[0]["category"] if category else None,
        reason=category[0]["reason"] if category else None,
    )
    db.add(appeal)
    await db.flush()

    await db.commit()

    if contains_explicit and not category:
        return ClassificationResponse(
            id=appeal.id,
            category=None,  # или как-то иначе обозначить отсутствие
            created_at=appeal.created_at
        )
    
    return ClassificationResponse(
        id=appeal.id,
        category=CategoryResult(category=category[0]["category"], reason=category[0]["reason"]) if category else None,
        created_at=appeal.created_at
    )

@app.get("/classify/{appeal_id}", response_model=AppealFromDB)

async def get_classification(
    appeal_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить обращение и его содержимое
    Args:
        id (int): id обращения
    """
    result = await db.execute(select(Appeal).where(Appeal.id == appeal_id))
    appeal = result.scalar_one_or_none()
    if not appeal:
        raise HTTPException(status_code=404, detail="Обращение не найдено")

    # Явно подгружаем связанные категории (если ещё не загружены)
    #await db.refresh(appeal, attribute_names=["category"])
    return AppealFromDB.model_validate(appeal)

@app.get("/analytics", response_model=AnalyticsResponse)
async def view_analytics(db: AsyncSession = Depends(get_db)):
    """
    Аналитика по всем обращением, плюс вывод соотношения зацензурированных 
    """
    return await get_analytics(db)