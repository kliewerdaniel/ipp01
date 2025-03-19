from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum, Float, JSON, func
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
    EXPERT = "expert"


class QuestionType(str, enum.Enum):
    """
    Enum for question types.
    """
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    GENERAL = "general"
    SITUATIONAL = "situational"
    CASE_STUDY = "case_study"
    BRAIN_TEASER = "brain_teaser"


class Question(Base):
    """
    Question model for storing interview questions.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    content = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    difficulty = Column(Enum(QuestionDifficulty), nullable=False, default=QuestionDifficulty.MEDIUM)
    
    # Categorization
    category = Column(String, nullable=True)  # Primary category (e.g., "arrays", "leadership")
    sub_category = Column(String, nullable=True)  # More specific subcategory
    tags = Column(String, nullable=True)  # Comma-separated tags or JSON string
    
    # Metadata
    is_ai_generated = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)  # Premium-only questions
    is_featured = Column(Boolean, default=False)  # Featured in highlights/recommendations
    position = Column(Integer, nullable=False, default=0)  # Order in the interview
    
    # Content and Answers
    expected_answer = Column(Text, nullable=True)  # Optional expected or example answer
    answer_keywords = Column(String, nullable=True)  # Important keywords that should be in a good answer
    follow_up_questions = Column(Text, nullable=True)  # Potential follow-up questions
    
    # Assessment criteria
    assessment_criteria = Column(JSON, nullable=True)  # JSON structure with assessment criteria and weights
    grading_rubric = Column(Text, nullable=True)  # Detailed grading guidelines
    max_score = Column(Float, default=100.0, nullable=False)  # Maximum score possible
    
    # Usage statistics
    times_used = Column(Integer, default=0)  # Number of times this question has been used
    avg_score = Column(Float, nullable=True)  # Average score users have received
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    interview_id = Column(String, ForeignKey("interview.id", ondelete="CASCADE"), nullable=True)  # Made nullable
    product_id = Column(String, ForeignKey("product.id", ondelete="SET NULL"), nullable=True)  # Link to product/platform
    
    # Relationships
    interview = relationship("Interview", back_populates="questions")
    product = relationship("Product", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")
