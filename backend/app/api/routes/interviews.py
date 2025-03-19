from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.interview import InterviewStatus, InterviewType
from app.schemas.question import QuestionResponse
from app.services.question import get_questions
from app.services.answer import get_answers
from app.schemas.answer import AnswerResponse

# Create interview schema - need to add this to schemas folder
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.interview import InterviewStatus, InterviewType

# Define these schemas in the appropriate file in the future
class InterviewBase(BaseModel):
    title: str
    description: Optional[str] = None
    interview_type: InterviewType


class InterviewCreate(InterviewBase):
    scheduled_at: Optional[datetime] = None


class InterviewUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    interview_type: Optional[InterviewType] = None
    status: Optional[InterviewStatus] = None
    scheduled_at: Optional[datetime] = None
    feedback: Optional[str] = None


class InterviewResponse(InterviewBase):
    id: str
    user_id: str
    status: InterviewStatus
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewWithQuestionsResponse(InterviewResponse):
    questions: List[QuestionResponse] = []


class InterviewWithAnswersResponse(InterviewResponse):
    answers: List[AnswerResponse] = []


# Interview service functions - should be moved to services folder
from app.models.interview import Interview

def get_interview_by_id(db: Session, id: str) -> Optional[Interview]:
    """
    Get an interview by ID.
    """
    return db.query(Interview).filter(Interview.id == id).first()


def get_user_interviews(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    status: Optional[InterviewStatus] = None,
    interview_type: Optional[InterviewType] = None
) -> List[Interview]:
    """
    Get interviews for a user with optional filtering.
    """
    query = db.query(Interview).filter(Interview.user_id == user_id)
    
    if status:
        query = query.filter(Interview.status == status)
    
    if interview_type:
        query = query.filter(Interview.interview_type == interview_type)
    
    return query.order_by(Interview.created_at.desc()).offset(skip).limit(limit).all()


def create_interview(db: Session, user_id: str, interview_data: InterviewCreate) -> Interview:
    """
    Create a new interview.
    """
    db_interview = Interview(
        user_id=user_id,
        title=interview_data.title,
        description=interview_data.description,
        interview_type=interview_data.interview_type,
        status=InterviewStatus.PENDING,
        scheduled_at=interview_data.scheduled_at
    )
    
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    
    return db_interview


def update_interview(db: Session, interview: Interview, interview_data: InterviewUpdate) -> Interview:
    """
    Update an interview.
    """
    for key, value in interview_data.model_dump(exclude_unset=True).items():
        setattr(interview, key, value)
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return interview


def start_interview(db: Session, interview: Interview) -> Interview:
    """
    Mark an interview as started.
    """
    interview.status = InterviewStatus.IN_PROGRESS
    interview.started_at = datetime.utcnow()
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return interview


def complete_interview(db: Session, interview: Interview, feedback: Optional[str] = None) -> Interview:
    """
    Mark an interview as completed.
    """
    interview.status = InterviewStatus.COMPLETED
    interview.completed_at = datetime.utcnow()
    
    if feedback:
        interview.feedback = feedback
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return interview


def cancel_interview(db: Session, interview: Interview) -> Interview:
    """
    Mark an interview as canceled.
    """
    interview.status = InterviewStatus.CANCELLED
    
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return interview


# Set up router
router = APIRouter()


@router.get("", response_model=List[InterviewResponse])
async def list_interviews(
    skip: int = 0,
    limit: int = 100,
    status: Optional[InterviewStatus] = None,
    interview_type: Optional[InterviewType] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a list of interviews for the current user.
    """
    interviews = get_user_interviews(
        db,
        user_id=current_user["id"],
        skip=skip,
        limit=limit,
        status=status,
        interview_type=interview_type
    )
    return interviews


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_new_interview(
    interview_data: InterviewCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new interview.
    """
    interview = create_interview(db, current_user["id"], interview_data)
    return interview


@router.get("/{interview_id}", response_model=InterviewWithQuestionsResponse)
async def get_interview(
    interview_id: str = Path(..., description="The ID of the interview to get"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single interview by ID with its questions.
    """
    interview = get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Check if the interview belongs to the current user
    if interview.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this interview"
        )
    
    # Get questions for this interview
    questions = get_questions(db, interview_id=interview_id)
    
    # Create response with questions
    response = InterviewWithQuestionsResponse.model_validate(interview)
    response.questions = questions
    
    return response


@router.get("/{interview_id}/answers", response_model=InterviewWithAnswersResponse)
async def get_interview_with_answers(
    interview_id: str = Path(..., description="The ID of the interview to get"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single interview by ID with its answers.
    """
    interview = get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Check if the interview belongs to the current user
    if interview.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this interview"
        )
    
    # Get answers for this interview
    answers = get_answers(db, interview_id=interview_id)
    
    # Create response with answers
    response = InterviewWithAnswersResponse.model_validate(interview)
    response.answers = answers
    
    return response


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview_endpoint(
    interview_data: InterviewUpdate,
    interview_id: str = Path(..., description="The ID of the interview to update"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing interview.
    """
    interview = get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Check if the interview belongs to the current user
    if interview.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this interview"
        )
    
    updated_interview = update_interview(db, interview, interview_data)
    return updated_interview


@router.post("/{interview_id}/start", response_model=InterviewResponse)
async def start_interview_endpoint(
    interview_id: str = Path(..., description="The ID of the interview to start"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an interview as started.
    """
    interview = get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Check if the interview belongs to the current user
    if interview.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this interview"
        )
    
    # Check if the interview is in a valid state to start
    if interview.status != InterviewStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interview cannot be started (current status: {interview.status})"
        )
    
    started_interview = start_interview(db, interview)
    return started_interview


@router.post("/{interview_id}/complete", response_model=InterviewResponse)
async def complete_interview_endpoint(
    interview_id: str = Path(..., description="The ID of the interview to complete"),
    feedback: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an interview as completed.
    """
    interview = get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Check if the interview belongs to the current user
    if interview.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this interview"
        )
    
    # Check if the interview is in a valid state to complete
    if interview.status != InterviewStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interview cannot be completed (current status: {interview.status})"
        )
    
    completed_interview = complete_interview(db, interview, feedback)
    return completed_interview


@router.post("/{interview_id}/cancel", response_model=InterviewResponse)
async def cancel_interview_endpoint(
    interview_id: str = Path(..., description="The ID of the interview to cancel"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an interview as canceled.
    """
    interview = get_interview_by_id(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found"
        )
    
    # Check if the interview belongs to the current user
    if interview.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this interview"
        )
    
    # Check if the interview is in a valid state to cancel
    if interview.status not in [InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interview cannot be canceled (current status: {interview.status})"
        )
    
    canceled_interview = cancel_interview(db, interview)
    return canceled_interview
