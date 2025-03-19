from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, func
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.db.base_class import Base


class Answer(Base):
    """
    Answer model for storing user responses to interview questions.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    content = Column(Text, nullable=True)  # Transcribed text
    audio_url = Column(String, nullable=True)  # URL to stored audio file
    duration = Column(Float, nullable=True)  # Duration of the audio in seconds
    feedback = Column(Text, nullable=True)  # AI-generated feedback
    feedback_score = Column(Float, nullable=True)  # Numerical score (e.g., 0-100)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    interview_id = Column(String, ForeignKey("interview.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String, ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="answers")
    question = relationship("Question", back_populates="answers")
