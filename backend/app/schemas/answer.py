from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AnswerBase(BaseModel):
    """
    Base schema for answer data.
    """
    content: Optional[str] = None  # Transcribed text
    audio_url: Optional[str] = None  # URL to stored audio file
    duration: Optional[float] = None  # Duration in seconds


class AnswerCreate(AnswerBase):
    """
    Schema for creating a new answer.
    """
    interview_id: str
    question_id: str


class AnswerUpdate(BaseModel):
    """
    Schema for updating answer data.
    """
    content: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    feedback: Optional[str] = None
    feedback_score: Optional[float] = Field(None, ge=0, le=100)


class AnswerResponse(AnswerBase):
    """
    Schema for answer response data.
    """
    id: str
    interview_id: str
    question_id: str
    feedback: Optional[str] = None
    feedback_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnswerFeedback(BaseModel):
    """
    Schema for AI-generated feedback for an answer.
    """
    feedback: str
    score: float = Field(..., ge=0, le=100)
    strengths: list[str]
    weaknesses: list[str]
    improvement_suggestions: list[str]


class AudioTranscriptionRequest(BaseModel):
    """
    Schema for requesting audio transcription.
    """
    audio_url: str
    language: str = "en"


class AudioTranscriptionResponse(BaseModel):
    """
    Schema for audio transcription response.
    """
    transcription: str
    confidence: Optional[float] = None
