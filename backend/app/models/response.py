from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON, Boolean, func
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.db.base_class import Base


class Response(Base):
    """
    Response model for storing user's audio responses to interview questions with associated feedback and assessment.
    """
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    
    # Audio and Transcription
    audio_path = Column(String, nullable=True)  # Path to stored audio file
    audio_url = Column(String, nullable=True)  # URL to access audio file
    audio_duration = Column(Float, nullable=True)  # Duration of audio in seconds
    file_size = Column(Integer, nullable=True)  # Size of audio file in bytes
    file_format = Column(String, nullable=True)  # Format of audio file (mp3, wav, etc.)
    transcription = Column(Text, nullable=True)  # Transcribed text from audio
    transcription_confidence = Column(Float, nullable=True)  # Confidence score of transcription
    
    # Self-assessment
    self_assessment_data = Column(JSON, nullable=True)  # User's self-evaluation in JSON format
    self_assessment_score = Column(Float, nullable=True)  # User's self-rating
    self_assessment_notes = Column(Text, nullable=True)  # User's notes about their performance
    
    # AI Feedback
    ai_feedback = Column(Text, nullable=True)  # AI-generated feedback
    ai_score = Column(Float, nullable=True)  # Overall AI-generated score
    ai_detailed_scores = Column(JSON, nullable=True)  # Detailed scoring across various dimensions
    ai_improvement_suggestions = Column(Text, nullable=True)  # Specific suggestions for improvement
    ai_feedback_metadata = Column(JSON, nullable=True)  # Additional metadata about the AI feedback
    
    # Status flags
    is_draft = Column(Boolean, default=False)  # Whether response is a draft
    is_submitted = Column(Boolean, default=False)  # Whether response has been officially submitted
    is_reviewed = Column(Boolean, default=False)  # Whether response has been reviewed
    is_featured = Column(Boolean, default=False)  # Whether response is featured as an example
    
    # Metrics
    word_count = Column(Integer, nullable=True)  # Number of words in transcription
    speaking_rate = Column(Float, nullable=True)  # Words per minute
    hesitation_count = Column(Integer, nullable=True)  # Number of hesitations/fillers
    
    # Timestamps
    recorded_at = Column(DateTime, nullable=True)  # When the audio was recorded
    transcribed_at = Column(DateTime, nullable=True)  # When the audio was transcribed
    feedback_generated_at = Column(DateTime, nullable=True)  # When feedback was generated
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String, ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    interview_id = Column(String, ForeignKey("interview.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    interview = relationship("Interview", back_populates="responses")
