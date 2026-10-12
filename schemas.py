from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class IssueDetail(BaseModel):
    id: str
    category: str  # bug, security, performance, style
    severity: str  # critical, warning, info
    line: int
    title: str
    description: str
    suggestion: str

class CodeReviewCreate(BaseModel):
    filename: Optional[str] = "untitled"
    language: str
    original_code: str

class CodeReviewResponse(BaseModel):
    id: int
    filename: str
    language: str
    original_code: str
    corrected_code: str
    score: int
    summary: Optional[str]
    issues: List[IssueDetail]
    created_at: datetime

    class Config:
        from_attributes = True
