from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging
import os
import json
from datetime import datetime

from app.models.answer import Answer
from app.models.question import Question
from app.models.interview import Interview
from app.schemas.answer import AnswerCreate, AnswerUpdate, AnswerFeedback
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_answer_by_id(db: Session, id: str) -> Optional[Answer]:
    """
    Get an answer by ID.
    """
    return db.query(Answer).filter(Answer.id == id).first()


def get_answers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    interview_id: Optional[str] = None,
    question_id: Optional[str] = None,
) -> List[Answer]:
    """
    Get answers with optional filtering.
    """
    query = db.query(Answer)
    
    if user_id:
        query = query.join(Interview, Answer.interview_id == Interview.id).filter(Interview.user_id == user_id)
    
    if interview_id:
        query = query.filter(Answer.interview_id == interview_id)
    
    if question_id:
        query = query.filter(Answer.question_id == question_id)
    
    # Order by creation date, newest first
    query = query.order_by(desc(Answer.created_at))
    
    return query.offset(skip).limit(limit).all()


def create_answer(db: Session, obj_in: AnswerCreate) -> Answer:
    """
    Create a new answer.
    """
    # Verify the question exists and belongs to the specified interview
    question = (
        db.query(Question)
        .filter(
            Question.id == obj_in.question_id,
            Question.interview_id == obj_in.interview_id
        )
        .first()
    )
    
    if not question:
        raise ValueError(f"Question with ID {obj_in.question_id} not found in interview {obj_in.interview_id}")
    
    # Create new answer
    db_obj = Answer(
        content=obj_in.content,
        audio_url=obj_in.audio_url,
        duration=obj_in.duration,
        interview_id=obj_in.interview_id,
        question_id=obj_in.question_id,
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Created new answer: {db_obj.id}")
    return db_obj


def update_answer(
    db: Session, 
    db_obj: Answer, 
    obj_in: Union[AnswerUpdate, Dict[str, Any]]
) -> Answer:
    """
    Update an answer.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)
    
    # Update answer with new data
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    logger.info(f"Updated answer: {db_obj.id}")
    return db_obj


def delete_answer(db: Session, db_obj: Answer) -> Answer:
    """
    Delete an answer.
    """
    answer_id = db_obj.id
    
    # Delete associated audio file if it exists
    if db_obj.audio_url and os.path.exists(db_obj.audio_url):
        try:
            os.remove(db_obj.audio_url)
            logger.info(f"Deleted audio file for answer {answer_id}")
        except Exception as e:
            logger.error(f"Failed to delete audio file: {str(e)}")
    
    db.delete(db_obj)
    db.commit()
    
    logger.info(f"Deleted answer: {answer_id}")
    return db_obj


async def generate_feedback(
    db: Session, 
    answer_id: str
) -> Optional[AnswerFeedback]:
    """
    Generate AI feedback for an answer.
    """
    # Get the answer with associated question
    answer = (
        db.query(Answer)
        .join(Question, Answer.question_id == Question.id)
        .filter(Answer.id == answer_id)
        .first()
    )
    
    if not answer:
        logger.error(f"Answer with ID {answer_id} not found")
        return None
    
    if not answer.content:
        logger.error(f"Answer {answer_id} has no content to evaluate")
        return None
    
    try:
        # Check if OpenAI API key is available
        if not settings.OPENAI_API_KEY:
            logger.error("OpenAI API key not configured")
            return None
        
        # In a real implementation, this would call the OpenAI API
        # For now, we'll simulate a response
        from openai import OpenAI
        import time
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Prepare message with context and transcription
        messages = [
            {"role": "system", "content": "You are an expert interview coach evaluating interview answers. Provide specific, constructive feedback on the candidate's answer along with a score from 0-100."},
            {"role": "user", "content": f"Question: {answer.question.content}\n\nCandidate's Answer: {answer.content}\n\nProvide feedback in this JSON format: {{\"feedback\": \"detailed feedback here\", \"score\": 85, \"strengths\": [\"strength1\", \"strength2\"], \"weaknesses\": [\"weakness1\", \"weakness2\"], \"improvement_suggestions\": [\"suggestion1\", \"suggestion2\"]}}"}
        ]
        
        # Get OpenAI response
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        feedback_data = json.loads(response.choices[0].message.content)
        
        # Create feedback object
        feedback = AnswerFeedback(
            feedback=feedback_data["feedback"],
            score=float(feedback_data["score"]),
            strengths=feedback_data["strengths"],
            weaknesses=feedback_data["weaknesses"],
            improvement_suggestions=feedback_data["improvement_suggestions"]
        )
        
        # Update answer with feedback
        answer.feedback = feedback.feedback
        answer.feedback_score = feedback.score
        
        db.add(answer)
        db.commit()
        db.refresh(answer)
        
        logger.info(f"Generated feedback for answer {answer_id} with score {feedback.score}")
        return feedback
        
    except Exception as e:
        logger.error(f"Error generating feedback: {str(e)}")
        return None


async def transcribe_audio(
    db: Session, 
    answer_id: str, 
    audio_path: str
) -> Optional[str]:
    """
    Transcribe audio file and update the answer.
    """
    answer = get_answer_by_id(db, answer_id)
    if not answer:
        logger.error(f"Answer with ID {answer_id} not found")
        return None
    
    try:
        # Check if audio file exists
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None
        
        # In a real implementation, this would use a speech recognition API/library
        # For now, we'll simulate a transcription
        import time
        import random
        
        # Simulate processing time
        time.sleep(1)
        
        # Sample transcribed text for testing
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        
        if question:
            # Generate a somewhat relevant response based on the question
            transcription = f"I believe the best approach to this is to carefully consider all aspects of the {question.category or 'situation'} before making a decision. Based on my experience, I would first analyze the requirements and then implement a solution that balances efficiency and maintainability."
        else:
            transcription = "Thank you for the question. Based on my experience, I would approach this situation by analyzing the key factors and implementing a strategic solution that addresses all stakeholders' needs."
        
        # Update the answer with transcription
        answer.content = transcription
        
        db.add(answer)
        db.commit()
        db.refresh(answer)
        
        logger.info(f"Transcribed audio for answer {answer_id}")
        return transcription
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return None


def get_answer_statistics(
    db: Session,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get statistics on answers.
    """
    query = db.query(Answer)
    
    if user_id:
        query = query.join(Interview, Answer.interview_id == Interview.id).filter(Interview.user_id == user_id)
    
    # Total answers
    total_answers = query.count()
    
    # Average feedback score
    avg_score = query.with_entities(func.avg(Answer.feedback_score)).scalar() or 0
    
    # Count of answers with feedback
    with_feedback = query.filter(Answer.feedback.isnot(None)).count()
    
    # Count by month (last 6 months)
    current_date = datetime.utcnow()
    month_counts = []
    
    for i in range(5, -1, -1):
        month = (current_date.month - i) % 12 or 12
        year = current_date.year - ((current_date.month - i - 1) // 12)
        
        count = (
            query
            .filter(
                func.extract('month', Answer.created_at) == month,
                func.extract('year', Answer.created_at) == year
            )
            .count()
        )
        
        month_counts.append({
            "month": month,
            "year": year,
            "count": count
        })
    
    return {
        "total_answers": total_answers,
        "with_feedback": with_feedback,
        "average_score": round(avg_score, 2),
        "monthly_counts": month_counts
    }
