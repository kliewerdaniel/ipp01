from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import uuid
import logging
from datetime import datetime

from app.db.session import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.schemas.answer import (
    AnswerResponse, 
    AnswerCreate, 
    AnswerUpdate, 
    AnswerFeedback,
    AudioTranscriptionRequest,
    AudioTranscriptionResponse
)
from app.services.answer import (
    get_answer_by_id,
    create_answer,
    update_answer,
    transcribe_audio,
    generate_feedback,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_audio(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(...),
    interview_id: str = Form(...),
    question_id: str = Form(...),
    duration: Optional[float] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an audio file for an answer.
    
    This endpoint will:
    1. Save the audio file
    2. Create an answer record
    3. Start the transcription process in the background
    """
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(str(settings.UPLOAD_DIR), exist_ok=True)
        
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.{audio_file.filename.split('.')[-1]}"
        filepath = os.path.join(str(settings.UPLOAD_DIR), filename)
        
        # Write the file
        with open(filepath, "wb") as f:
            content = await audio_file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB"
                )
            f.write(content)
        
        # Create the answer record
        answer = create_answer(
            db,
            AnswerCreate(
                interview_id=interview_id,
                question_id=question_id,
                audio_url=filepath,
                duration=duration
            )
        )
        
        # Start transcription in the background
        background_tasks.add_task(
            transcribe_audio,
            db=db,
            answer_id=answer.id,
            audio_path=filepath
        )
        
        return {
            "id": answer.id,
            "audio_url": filepath,
            "status": "processing",
            "message": "Audio uploaded successfully. Transcription is being processed."
        }
    
    except Exception as e:
        logger.error(f"Error uploading audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading audio: {str(e)}"
        )


@router.post("/transcribe", response_model=AudioTranscriptionResponse)
async def transcribe_audio_endpoint(
    transcription_request: AudioTranscriptionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Transcribe an audio file.
    """
    try:
        # Check if file exists
        if not os.path.exists(transcription_request.audio_url):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found"
            )
        
        # In a real implementation, this would use a speech recognition service
        # For this example, we'll return a placeholder
        return AudioTranscriptionResponse(
            transcription="This is a simulated transcription for the audio file.",
            confidence=0.95
        )
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transcribing audio: {str(e)}"
        )


@router.post("/{answer_id}/feedback", response_model=AnswerFeedback)
async def generate_answer_feedback(
    answer_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI feedback for an answer.
    """
    # Get the answer
    answer = get_answer_by_id(db, answer_id)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found"
        )
    
    # Check if the answer has content
    if not answer.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer has no content to evaluate"
        )
    
    try:
        # Generate feedback
        feedback = await generate_feedback(db, answer_id)
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate feedback"
            )
        
        return feedback
    
    except Exception as e:
        logger.error(f"Error generating feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating feedback: {str(e)}"
        )


@router.get("/answers/{answer_id}", response_model=AnswerResponse)
async def get_answer(
    answer_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an answer by ID.
    """
    answer = get_answer_by_id(db, answer_id)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found"
        )
    
    return answer


@router.put("/answers/{answer_id}", response_model=AnswerResponse)
async def update_answer_endpoint(
    answer_id: str,
    answer_update: AnswerUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an answer.
    """
    answer = get_answer_by_id(db, answer_id)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found"
        )
    
    updated_answer = update_answer(db, db_obj=answer, obj_in=answer_update)
    return updated_answer
