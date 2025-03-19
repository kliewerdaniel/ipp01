from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum, func
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum

from app.db.base_class import Base


class QuestionDifficulty(str, enum.Enum):
    """
    Enum for question difficulty levels.
    """
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, enum.Enum):
    """
    Enum for question types.
    """
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    GENERAL = "general"


class Question(Base):
    """
    Question model for storing interview questions.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    content = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    difficulty = Column(Enum(QuestionDifficulty), nullable=False, default=QuestionDifficulty.MEDIUM)
    category = Column(String, nullable=True)  # E.g., "arrays", "algorithms", "leadership"
    is_ai_generated = Column(Boolean, default=False)
    expected_answer = Column(Text, nullable=True)  # Optional expected or example answer
    position = Column(Integer, nullable=False, default=0)  # Order in the interview
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    interview_id = Column(String, ForeignKey("interview.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
