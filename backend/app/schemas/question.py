from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.question import QuestionDifficulty, QuestionType


class QuestionBase(BaseModel):
    """
    Base schema for question data.
    """
    content: str
    question_type: QuestionType
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    category: Optional[str] = None
    expected_answer: Optional[str] = None
    position: int = 0


class QuestionCreate(QuestionBase):
    """
    Schema for creating a new question.
    """
    interview_id: str


class QuestionUpdate(BaseModel):
    """
    Schema for updating question data.
    """
    content: Optional[str] = None
    question_type: Optional[QuestionType] = None
    difficulty: Optional[QuestionDifficulty] = None
    category: Optional[str] = None
    expected_answer: Optional[str] = None
    position: Optional[int] = None


class QuestionResponse(QuestionBase):
    """
    Schema for question response data.
    """
    id: str
    interview_id: str
    is_ai_generated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionSearch(BaseModel):
    """
    Schema for searching questions.
    """
    query: Optional[str] = None
    question_type: Optional[QuestionType] = None
    difficulty: Optional[QuestionDifficulty] = None
    category: Optional[str] = None
    limit: int = 20
    offset: int = 0


class BulkQuestionsCreate(BaseModel):
    """
    Schema for creating multiple questions at once.
    """
    interview_id: str
    questions: List[QuestionBase]


class CategoryCount(BaseModel):
    """
    Schema for returning category counts.
    """
    category: str
    count: int


class QuestionStatistics(BaseModel):
    """
    Schema for question statistics.
    """
    total_questions: int
    by_difficulty: Dict[str, int]
    by_type: Dict[str, int]
    by_category: List[CategoryCount]
