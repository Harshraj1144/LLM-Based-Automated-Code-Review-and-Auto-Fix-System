from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app import models, schemas

async def get_reviews(db: AsyncSession):
    result = await db.execute(select(models.CodeReview).order_by(models.CodeReview.created_at.desc()))
    return result.scalars().all()

async def get_review(db: AsyncSession, review_id: int):
    result = await db.execute(select(models.CodeReview).filter(models.CodeReview.id == review_id))
    return result.scalar_one_or_none()

async def create_review(db: AsyncSession, review: schemas.CodeReviewCreate, analysis: dict):
    db_review = models.CodeReview(
        filename=review.filename or "untitled",
        language=review.language,
        original_code=review.original_code,
        corrected_code=analysis.get("corrected_code", review.original_code),
        score=analysis.get("score", 100),
        summary=analysis.get("summary", ""),
        issues=analysis.get("issues", [])
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review

async def delete_review(db: AsyncSession, review_id: int):
    db_review = await get_review(db, review_id)
    if db_review:
        await db.delete(db_review)
        await db.commit()
        return True
    return False
