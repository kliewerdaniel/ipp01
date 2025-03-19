from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, func
from sqlalchemy.orm import relationship
from uuid import uuid4
import enum

from app.db.base_class import Base


class InterviewStatus(str, enum.Enum):
    """
    Enum for interview status.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewType(str, enum.Enum):
    """
    Enum for interview types.
    """
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CASE_STUDY = "case_study"
    MOCK = "mock"
    CUSTOM = "custom"


class Interview(Base):
    """
    Interview model for storing interview sessions.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    interview_type = Column(Enum(InterviewType), nullable=False)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.PENDING, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="interview", cascade="all, delete-orphan")
