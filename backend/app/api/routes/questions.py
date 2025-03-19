from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.question import QuestionDifficulty, QuestionType
from app.schemas.question import (
    QuestionResponse, 
    QuestionCreate, 
    QuestionUpdate, 
    QuestionSearch,
    BulkQuestionsCreate,
    QuestionStatistics,
    CategoryCount
)
from app.services.question import (
    get_question_by_id,
    get_questions,
    search_questions,
    create_question,
    create_bulk_questions,
    update_question,
    delete_question,
    get_question_categories,
    get_question_statistics,
    reorder_questions
)

router = APIRouter()


@router.get("", response_model=List[QuestionResponse])
async def list_questions(
    skip: int = 0,
    limit: int = 100,
    interview_id: Optional[str] = None,
    question_type: Optional[QuestionType] = None,
    difficulty: Optional[QuestionDifficulty] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a list of questions with optional filtering.
    """
    questions = get_questions(
        db,
        skip=skip,
        limit=limit,
        interview_id=interview_id,
        question_type=question_type,
        difficulty=difficulty,
        category=category
    )
    return questions


@router.post("/search", response_model=dict)
async def search_questions_endpoint(
    search_params: QuestionSearch,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search questions with various filters.
    """
    questions, total_count = search_questions(db, search_params)
    return {
        "questions": questions,
        "total": total_count,
        "limit": search_params.limit,
        "offset": search_params.offset
    }


@router.get("/categories", response_model=List[CategoryCount])
async def get_all_categories(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all unique categories with counts.
    """
    return get_question_categories(db)


@router.get("/statistics", response_model=QuestionStatistics)
async def get_question_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics on questions.
    """
    return get_question_statistics(db)


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str = Path(..., description="The ID of the question to get"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single question by ID.
    """
    question = get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    return question


@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question_endpoint(
    question_in: QuestionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new question.
    """
    try:
        question = create_question(db, question_in)
        return question
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bulk", response_model=List[QuestionResponse], status_code=status.HTTP_201_CREATED)
async def create_bulk_questions_endpoint(
    questions_in: BulkQuestionsCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create multiple questions at once.
    """
    try:
        questions = create_bulk_questions(
            db, 
            interview_id=questions_in.interview_id, 
            questions=questions_in.questions
        )
        return questions
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question_endpoint(
    question_in: QuestionUpdate,
    question_id: str = Path(..., description="The ID of the question to update"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing question.
    """
    question = get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    updated_question = update_question(db, db_obj=question, obj_in=question_in)
    return updated_question


@router.delete("/{question_id}", response_model=QuestionResponse)
async def delete_question_endpoint(
    question_id: str = Path(..., description="The ID of the question to delete"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a question.
    """
    question = get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    deleted_question = delete_question(db, db_obj=question)
    return deleted_question


@router.post("/reorder", response_model=List[QuestionResponse])
async def reorder_questions_endpoint(
    interview_id: str = Query(..., description="Interview ID"),
    question_ids: List[str] = Query(..., description="List of question IDs in the desired order"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reorder questions within an interview.
    """
    try:
        questions = reorder_questions(db, interview_id=interview_id, question_ids=question_ids)
        return questions
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
