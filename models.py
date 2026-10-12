from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from backend.app.database import Base

class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, default="untitled")
    language = Column(String, nullable=False)
    original_code = Column(Text, nullable=False)
    corrected_code = Column(Text, nullable=False)
    score = Column(Integer, nullable=False, default=100)
    summary = Column(Text, nullable=True)
    issues = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
