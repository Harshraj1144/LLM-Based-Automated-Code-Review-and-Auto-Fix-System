from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.app import crud, schemas, llm
from backend.app.database import get_db

router = APIRouter(prefix="/api/reviews", tags=["reviews"])

@router.post("", response_model=schemas.CodeReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(review: schemas.CodeReviewCreate, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Analyze using LLM service
        analysis_result = await llm.analyze_code(review.original_code, review.language)
        
        # 2. Save result in Database
        db_review = await crud.create_review(db, review, analysis_result)
        return db_review
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code analysis or storage failed: {str(e)}"
        )

@router.get("", response_model=List[schemas.CodeReviewResponse])
async def list_reviews(db: AsyncSession = Depends(get_db)):
    reviews = await crud.get_reviews(db)
    return reviews

@router.get("/{review_id}", response_model=schemas.CodeReviewResponse)
async def get_review(review_id: int, db: AsyncSession = Depends(get_db)):
    review = await crud.get_review(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Code review not found"
        )
    return review

@router.delete("/{review_id}")
async def delete_review(review_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_review(db, review_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Code review not found"
        )
    return {"status": "success", "message": "Code review history item deleted successfully"}
