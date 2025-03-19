from typing import Optional, List, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, and_, or_
import logging

from app.models.question import Question, QuestionDifficulty, QuestionType
from app.models.interview import Interview
from app.schemas.question import (
    QuestionCreate, 
    QuestionUpdate, 
    QuestionSearch,
    CategoryCount
)

logger = logging.getLogger(__name__)


def get_question_by_id(db: Session, id: str) -> Optional[Question]:
    """
    Get a question by ID.
    """
    return db.query(Question).filter(Question.id == id).first()


def get_questions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    interview_id: Optional[str] = None,
    question_type: Optional[QuestionType] = None,
    difficulty: Optional[QuestionDifficulty] = None,
    category: Optional[str] = None,
) -> List[Question]:
    """
    Get questions with optional filtering.
    """
    query = db.query(Question)
    
    if interview_id:
        query = query.filter(Question.interview_id == interview_id)
    
    if question_type:
        query = query.filter(Question.question_type == question_type)
    
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    
    if category:
        query = query.filter(Question.category == category)
    
    # Order by position for ordering in the interview
    query = query.order_by(Question.position)
    
    return query.offset(skip).limit(limit).all()


def search_questions(
    db: Session,
    search_params: QuestionSearch
) -> Tuple[List[Question], int]:
    """
    Search questions with various filters and text search.
    Returns a tuple of (questions, total_count)
    """
    query = db.query(Question)
    
    # Apply filters
    if search_params.question_type:
        query = query.filter(Question.question_type == search_params.question_type)
    
    if search_params.difficulty:
        query = query.filter(Question.difficulty == search_params.difficulty)
    
    if search_params.category:
        query = query.filter(Question.category == search_params.category)
    
    # Apply text search if query provided
    if search_params.query:
        search_term = f"%{search_params.query}%"
        query = query.filter(
            or_(
                Question.content.ilike(search_term),
                Question.expected_answer.ilike(search_term),
                Question.category.ilike(search_term)
            )
        )
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination
    questions = query.order_by(Question.position).offset(search_params.offset).limit(search_params.limit).all()
    
    return questions, total_count


def create_question(db: Session, obj_in: QuestionCreate) -> Question:
    """
    Create a new question.
    """
    # Verify that the interview exists
    interview = db.query(Interview).filter(Interview.id == obj_in.interview_id).first()
    if not interview:
        raise ValueError(f"Interview with ID {obj_in.interview_id} not found")
    
    # Create new question
    db_obj = Question(
        content=obj_in.content,
        question_type=obj_in.question_type,
        difficulty=obj_in.difficulty,
        category=obj_in.category,
        expected_answer=obj_in.expected_answer,
        position=obj_in.position,
        interview_id=obj_in.interview_id,
        is_ai_generated=False,  # Default to false, can be set later
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Created new question: {db_obj.id}")
    return db_obj


def create_bulk_questions(
    db: Session, 
    interview_id: str, 
    questions: List[Question]
) -> List[Question]:
    """
    Create multiple questions at once for an interview.
    """
    # Verify that the interview exists
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise ValueError(f"Interview with ID {interview_id} not found")
    
    # Create and add all questions
    db_objs = []
    for i, question in enumerate(questions):
        db_obj = Question(
            content=question.content,
            question_type=question.question_type,
            difficulty=question.difficulty,
            category=question.category,
            expected_answer=question.expected_answer,
            position=question.position or i,  # Use provided position or index
            interview_id=interview_id,
            is_ai_generated=False,
        )
        db.add(db_obj)
        db_objs.append(db_obj)
    
    db.commit()
    
    # Refresh all objects
    for db_obj in db_objs:
        db.refresh(db_obj)
    
    logger.info(f"Created {len(db_objs)} questions for interview {interview_id}")
    return db_objs


def update_question(
    db: Session, 
    db_obj: Question, 
    obj_in: Union[QuestionUpdate, Dict[str, Any]]
) -> Question:
    """
    Update a question.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Update question with new data
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Updated question: {db_obj.id}")
    return db_obj


def delete_question(db: Session, db_obj: Question) -> Question:
    """
    Delete a question.
    """
    question_id = db_obj.id
    db.delete(db_obj)
    db.commit()
    
    logger.info(f"Deleted question: {question_id}")
    return db_obj


def get_question_categories(db: Session) -> List[CategoryCount]:
    """
    Get all unique categories with their question counts.
    """
    results = (
        db.query(
            Question.category,
            func.count(Question.id).label("count")
        )
        .filter(Question.category.isnot(None))
        .group_by(Question.category)
        .order_by(func.count(Question.id).desc())
        .all()
    )
    
    return [
        CategoryCount(category=category, count=count)
        for category, count in results
    ]


def get_question_statistics(db: Session) -> Dict[str, Any]:
    """
    Get statistics on questions (counts by difficulty, type, etc.).
    """
    # Total questions count
    total_questions = db.query(func.count(Question.id)).scalar()
    
    # Count by difficulty
    difficulty_counts = (
        db.query(
            Question.difficulty,
            func.count(Question.id).label("count")
        )
        .group_by(Question.difficulty)
        .all()
    )
    
    difficulty_dict = {
        str(d.value): count for d, count in difficulty_counts
    }
    
    # Count by type
    type_counts = (
        db.query(
            Question.question_type,
            func.count(Question.id).label("count")
        )
        .group_by(Question.question_type)
        .all()
    )
    
    type_dict = {
        str(t.value): count for t, count in type_counts
    }
    
    # Categories with counts
    category_counts = get_question_categories(db)
    
    return {
        "total_questions": total_questions,
        "by_difficulty": difficulty_dict,
        "by_type": type_dict,
        "by_category": category_counts
    }


def reorder_questions(db: Session, interview_id: str, question_ids: List[str]) -> List[Question]:
    """
    Reorder questions within an interview.
    """
    # Verify interview exists
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise ValueError(f"Interview with ID {interview_id} not found")
    
    # Update positions based on the provided order
    questions = []
    for i, question_id in enumerate(question_ids):
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.interview_id == interview_id
        ).first()
        
        if question:
            question.position = i
            db.add(question)
            questions.append(question)
    
    db.commit()
    
    # Refresh all questions
    for question in questions:
        db.refresh(question)
    
    logger.info(f"Reordered {len(questions)} questions for interview {interview_id}")
    return questions
