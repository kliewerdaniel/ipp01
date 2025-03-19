from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import os
import uuid
import logging
from datetime import datetime
from app.services.transcription import default_transcription_service, TranscriptionProvider, TranscriptionServiceFactory
from app.services.ai import default_ai_service, AIProvider, AIServiceFactory
from app.services import audio_utils

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
    preprocess_audio: bool = Form(True),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an audio file for an answer.
    
    This endpoint will:
    1. Save the audio file
    2. Preprocess the audio for optimal transcription (if requested)
    3. Create an answer record
    4. Start the transcription process in the background
    """
    try:
        # Create upload directory if it doesn't exist
        upload_dir = str(settings.UPLOAD_DIR)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate a unique filename and save the original file
        orig_ext = audio_file.filename.split('.')[-1].lower()
        unique_id = uuid.uuid4()
        original_filename = f"{unique_id}_original.{orig_ext}"
        original_filepath = os.path.join(upload_dir, original_filename)
        
        # Write the file
        with open(original_filepath, "wb") as f:
            content = await audio_file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB"
                )
            f.write(content)
        
        # Process the audio if requested
        filepath = original_filepath
        if preprocess_audio:
            try:
                # Process the audio for optimal transcription
                processed_filename = f"{unique_id}_processed.wav"
                processed_filepath = os.path.join(upload_dir, processed_filename)
                
                # Preprocess the audio file
                filepath = audio_utils.prepare_for_transcription(
                    input_path=original_filepath,
                    output_path=processed_filepath,
                    normalize=True,
                    remove_background_noise=False,  # More aggressive processing can be enabled if needed
                    target_format="wav",
                    target_sample_rate=16000,  # 16kHz is optimal for most speech recognition
                    target_channels=1  # Mono is better for speech recognition
                )
                
                # Get audio information for the processed file
                audio_info = audio_utils.get_audio_info(filepath)
                
                # Update duration if not provided
                if duration is None and "duration" in audio_info:
                    duration = audio_info["duration"]
                    
                logger.info(f"Preprocessed audio file: {filepath}, duration: {duration}s")
                
            except audio_utils.AudioProcessingError as e:
                # If preprocessing fails, use the original file
                logger.warning(f"Audio preprocessing failed, using original file: {str(e)}")
                filepath = original_filepath
        
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
    Transcribe an audio file using the configured transcription service.
    """
    try:
        # Check if file exists
        if not os.path.exists(transcription_request.audio_url):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found"
            )
        
        # Use the transcription service to transcribe the audio
        result = await default_transcription_service.transcribe_file(
            file_path=transcription_request.audio_url,
            language=transcription_request.language
        )
        
        return AudioTranscriptionResponse(
            transcription=result.text,
            confidence=result.confidence
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
    feedback_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI feedback for an answer.
    
    Args:
        answer_id: The ID of the answer to generate feedback for
        feedback_type: Optional type of feedback (general, technical, behavioral)
            If not provided, it will be inferred from the question category
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
        feedback = await generate_feedback(db, answer_id, feedback_type)
        
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


@router.get("/service-info")
async def get_service_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get information about the currently configured transcription and AI services.
    
    This is useful for debugging and for displaying service information in the UI.
    """
    transcription_service = default_transcription_service
    ai_service = default_ai_service
    
    # Check if FFmpeg is installed
    ffmpeg_installed = audio_utils.check_ffmpeg_installed()
    
    return {
        "transcription": {
            "provider": transcription_service.name,
            "supports_streaming": transcription_service.supports_streaming,
            "supported_formats": transcription_service.supported_formats,
            "supported_languages": transcription_service.supported_languages
        },
        "ai": {
            "provider": ai_service.name,
            "available_models": ai_service.available_models,
            "default_model": ai_service.default_model
        },
        "audio_processing": {
            "ffmpeg_installed": ffmpeg_installed,
            "can_preprocess_audio": ffmpeg_installed
        }
    }


@router.post("/audio/process")
async def process_audio_file(
    audio_file: UploadFile = File(...),
    normalize: bool = Form(True),
    remove_noise: bool = Form(False),
    remove_silence: bool = Form(False),
    target_format: str = Form("wav"),
    current_user: dict = Depends(get_current_user)
):
    """
    Process an audio file with various optimizations.
    
    Args:
        audio_file: The audio file to process
        normalize: Whether to normalize audio levels
        remove_noise: Whether to attempt noise reduction
        remove_silence: Whether to remove silence
        target_format: Target audio format
    
    Returns:
        URL to the processed audio file
    """
    try:
        # Check if FFmpeg is installed
        if not audio_utils.check_ffmpeg_installed():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FFmpeg is not installed, audio processing unavailable"
            )
            
        # Create upload directory if it doesn't exist
        upload_dir = str(settings.UPLOAD_DIR)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the uploaded file
        temp_filepath = os.path.join(upload_dir, f"temp_{uuid.uuid4()}.{audio_file.filename.split('.')[-1]}")
        with open(temp_filepath, "wb") as f:
            content = await audio_file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB"
                )
            f.write(content)
        
        # Process the audio
        processed_filepath = os.path.join(upload_dir, f"processed_{uuid.uuid4()}.{target_format}")
        
        if remove_silence and audio_utils.check_ffmpeg_installed():
            # Remove silence first if requested
            silence_removed_path = audio_utils.remove_silence(
                input_path=temp_filepath,
                silence_threshold=-50.0  # Default threshold
            )
            temp_filepath = silence_removed_path
        
        # Prepare the audio file with requested processing
        processed_filepath = audio_utils.prepare_for_transcription(
            input_path=temp_filepath,
            output_path=processed_filepath,
            normalize=normalize,
            remove_background_noise=remove_noise,
            target_format=target_format,
            target_sample_rate=16000,
            target_channels=1
        )
        
        # Get audio information
        audio_info = audio_utils.get_audio_info(processed_filepath)
        
        # Clean up temporary file
        if os.path.exists(temp_filepath) and temp_filepath != processed_filepath:
            os.unlink(temp_filepath)
        
        return {
            "processed_url": processed_filepath,
            "original_filename": audio_file.filename,
            "processed_format": target_format,
            "audio_info": audio_info,
            "processing_applied": {
                "normalized": normalize,
                "noise_removed": remove_noise,
                "silence_removed": remove_silence
            }
        }
    
    except audio_utils.AudioProcessingError as e:
        logger.error(f"Audio processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Audio processing error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio: {str(e)}"
        )
