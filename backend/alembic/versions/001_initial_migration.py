"""initial migration

Revision ID: 001
Revises: 
Create Date: 2025-03-19 15:37:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float, JSON, Enum

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables from scratch"""
    
    # Create product table
    op.create_table(
        'product',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('custom_domains', sa.String(), nullable=True),
        sa.Column('theme_settings', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), default=True, nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('access_code', sa.String(), nullable=True),
        sa.Column('custom_welcome_message', sa.Text(), nullable=True),
        sa.Column('custom_footer', sa.Text(), nullable=True),
        sa.Column('custom_css', sa.Text(), nullable=True),
        sa.Column('custom_js', sa.Text(), nullable=True),
        sa.Column('total_users', sa.Integer(), default=0, nullable=True),
        sa.Column('total_interviews', sa.Integer(), default=0, nullable=True),
        sa.Column('total_questions', sa.Integer(), default=0, nullable=True),
        sa.Column('average_rating', sa.Float(), nullable=True),
        sa.Column('owner_id', sa.String(), nullable=True),
        sa.Column('admin_emails', sa.String(), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('max_interviews_per_user', sa.Integer(), nullable=True),
        sa.Column('max_questions_per_interview', sa.Integer(), nullable=True),
        sa.Column('max_storage_gb', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_product_id'), 'product', ['id'], unique=False)

    # Create subscription_plan table
    op.create_table(
        'subscription_plan',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_monthly', sa.Float(), nullable=False),
        sa.Column('price_yearly', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(), default='USD', nullable=False),
        sa.Column('trial_days', sa.Integer(), default=0, nullable=False),
        sa.Column('setup_fee', sa.Float(), default=0.0, nullable=False),
        sa.Column('max_interviews', sa.Integer(), nullable=True),
        sa.Column('max_questions_per_interview', sa.Integer(), nullable=True),
        sa.Column('max_storage_gb', sa.Float(), nullable=True),
        sa.Column('max_audio_length_mins', sa.Integer(), nullable=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('is_ai_feedback_enabled', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_export_enabled', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_team_access_enabled', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_premium_questions_enabled', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_custom_branding_enabled', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_public', sa.Boolean(), default=True, nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('highlight', sa.Boolean(), default=False, nullable=True),
        sa.Column('sort_order', sa.Integer(), default=0, nullable=True),
        sa.Column('stripe_price_id', sa.String(), nullable=True),
        sa.Column('stripe_product_id', sa.String(), nullable=True),
        sa.Column('product_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_subscription_plan_id'), 'subscription_plan', ['id'], unique=False)

    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        
        # Profile information
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('profile_image_url', sa.String(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('job_title', sa.String(), nullable=True),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('years_of_experience', sa.Integer(), nullable=True),
        sa.Column('skills', sa.String(), nullable=True),
        
        # Subscription status
        sa.Column('current_subscription_id', sa.String(), nullable=True),
        sa.Column('subscription_status', sa.String(), nullable=True),
        
        # Auth status
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('is_superuser', sa.Boolean(), default=False, nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        
        # Settings and preferences
        sa.Column('email_notifications', sa.Boolean(), default=True, nullable=True),
        sa.Column('interface_language', sa.String(), default='en', nullable=False),
        sa.Column('timezone', sa.String(), default='UTC', nullable=False),
        
        # Timestamps
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

    # Create interview table
    op.create_table(
        'interview',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('interview_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), default='pending', nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_id'), 'interview', ['id'], unique=False)

    # Create subscription table
    op.create_table(
        'subscription',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), default='active', nullable=False),
        sa.Column('billing_period', sa.String(), default='monthly', nullable=False),
        sa.Column('billing_email', sa.String(), nullable=True),
        sa.Column('billing_name', sa.String(), nullable=True),
        sa.Column('billing_address', sa.Text(), nullable=True),
        sa.Column('billing_country', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), default=0.0, nullable=False),
        sa.Column('currency', sa.String(), default='USD', nullable=False),
        sa.Column('payment_method_id', sa.String(), nullable=True),
        sa.Column('payment_method_type', sa.String(), nullable=True),
        sa.Column('last_four', sa.String(), nullable=True),
        sa.Column('card_brand', sa.String(), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('trial_start', sa.DateTime(), nullable=True),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), default=False, nullable=True),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('next_invoice_date', sa.DateTime(), nullable=True),
        sa.Column('invoice_data', sa.JSON(), nullable=True),
        sa.Column('latest_invoice_id', sa.String(), nullable=True),
        sa.Column('usage_stats', sa.JSON(), nullable=True),
        sa.Column('subscription_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('subscription_plan_id', sa.String(), nullable=True),
        sa.Column('product_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['subscription_plan_id'], ['subscription_plan.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )
    op.create_index(op.f('ix_subscription_id'), 'subscription', ['id'], unique=False)

    # Create question table
    op.create_table(
        'question',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(), nullable=False),
        sa.Column('difficulty', sa.String(), default='medium', nullable=False),
        
        # Categorization
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('sub_category', sa.String(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        
        # Metadata
        sa.Column('is_ai_generated', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_premium', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_featured', sa.Boolean(), default=False, nullable=True),
        sa.Column('position', sa.Integer(), default=0, nullable=False),
        
        # Content and Answers
        sa.Column('expected_answer', sa.Text(), nullable=True),
        sa.Column('answer_keywords', sa.String(), nullable=True),
        sa.Column('follow_up_questions', sa.Text(), nullable=True),
        
        # Assessment criteria
        sa.Column('assessment_criteria', sa.JSON(), nullable=True),
        sa.Column('grading_rubric', sa.Text(), nullable=True),
        sa.Column('max_score', sa.Float(), default=100.0, nullable=False),
        
        # Usage statistics
        sa.Column('times_used', sa.Integer(), default=0, nullable=True),
        sa.Column('avg_score', sa.Float(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Foreign keys
        sa.Column('interview_id', sa.String(), nullable=True),
        sa.Column('product_id', sa.String(), nullable=True),
        
        sa.ForeignKeyConstraint(['interview_id'], ['interview.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_id'), 'question', ['id'], unique=False)

    # Create answer table
    op.create_table(
        'answer',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('audio_url', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('feedback_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('interview_id', sa.String(), nullable=False),
        sa.Column('question_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interview.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['question.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answer_id'), 'answer', ['id'], unique=False)

    # Create response table
    op.create_table(
        'response',
        sa.Column('id', sa.String(), nullable=False),
        
        # Audio and Transcription
        sa.Column('audio_path', sa.String(), nullable=True),
        sa.Column('audio_url', sa.String(), nullable=True),
        sa.Column('audio_duration', sa.Float(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_format', sa.String(), nullable=True),
        sa.Column('transcription', sa.Text(), nullable=True),
        sa.Column('transcription_confidence', sa.Float(), nullable=True),
        
        # Self-assessment
        sa.Column('self_assessment_data', sa.JSON(), nullable=True),
        sa.Column('self_assessment_score', sa.Float(), nullable=True),
        sa.Column('self_assessment_notes', sa.Text(), nullable=True),
        
        # AI Feedback
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('ai_score', sa.Float(), nullable=True),
        sa.Column('ai_detailed_scores', sa.JSON(), nullable=True),
        sa.Column('ai_improvement_suggestions', sa.Text(), nullable=True),
        sa.Column('ai_feedback_metadata', sa.JSON(), nullable=True),
        
        # Status flags
        sa.Column('is_draft', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_submitted', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_reviewed', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_featured', sa.Boolean(), default=False, nullable=True),
        
        # Metrics
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('speaking_rate', sa.Float(), nullable=True),
        sa.Column('hesitation_count', sa.Integer(), nullable=True),
        
        # Timestamps
        sa.Column('recorded_at', sa.DateTime(), nullable=True),
        sa.Column('transcribed_at', sa.DateTime(), nullable=True),
        sa.Column('feedback_generated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Foreign keys
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('question_id', sa.String(), nullable=False),
        sa.Column('interview_id', sa.String(), nullable=True),
        
        sa.ForeignKeyConstraint(['interview_id'], ['interview.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['question.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_response_id'), 'response', ['id'], unique=False)

    # Create billing_history table
    op.create_table(
        'billing_history',
        sa.Column('id', sa.String(), nullable=False),
        
        # Event information
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Amount and payment
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(), default='USD', nullable=True),
        sa.Column('payment_status', sa.String(), nullable=True),
        
        # Payment details
        sa.Column('payment_method_type', sa.String(), nullable=True),
        sa.Column('payment_last_four', sa.String(), nullable=True),
        sa.Column('payment_brand', sa.String(), nullable=True),
        
        # Invoice details
        sa.Column('invoice_id', sa.String(), nullable=True),
        sa.Column('invoice_number', sa.String(), nullable=True),
        sa.Column('invoice_url', sa.String(), nullable=True),
        sa.Column('receipt_url', sa.String(), nullable=True),
        
        # For refunds
        sa.Column('refund_id', sa.String(), nullable=True),
        sa.Column('refunded_amount', sa.Float(), nullable=True),
        sa.Column('refund_reason', sa.Text(), nullable=True),
        
        # For subscription changes
        sa.Column('previous_plan_id', sa.String(), nullable=True),
        sa.Column('new_plan_id', sa.String(), nullable=True),
        
        # External IDs
        sa.Column('stripe_event_id', sa.String(), nullable=True),
        sa.Column('stripe_invoice_id', sa.String(), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(), nullable=True),
        sa.Column('stripe_charge_id', sa.String(), nullable=True),
        
        # Metadata
        sa.Column('event_metadata', sa.JSON(), nullable=True),
        sa.Column('is_visible_to_customer', sa.Boolean(), default=True, nullable=True),
        
        # Timestamps
        sa.Column('event_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Foreign keys
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('subscription_id', sa.String(), nullable=True),
        
        sa.ForeignKeyConstraint(['subscription_id'], ['subscription.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_billing_history_id'), 'billing_history', ['id'], unique=False)


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('billing_history')
    op.drop_table('response')
    op.drop_table('answer')
    op.drop_table('question')
    op.drop_table('subscription')
    op.drop_table('interview')
    op.drop_table('user')
    op.drop_table('subscription_plan')
    op.drop_table('product')
