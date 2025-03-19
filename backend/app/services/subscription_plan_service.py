import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.subscription_plan import SubscriptionPlan
from app.models.product import Product
from app.schemas.subscription import PlanDetails, PlanFeature
from app.services.stripe_service import create_product, create_price

logger = logging.getLogger(__name__)

# Plan configurations
SUBSCRIPTION_PLANS = [
    {
        "name": "Free",
        "code": "free",
        "description": "Basic access to practice interviews",
        "price_monthly": 0.0,
        "price_yearly": 0.0,
        "currency": "USD",
        "trial_days": 0,
        "setup_fee": 0.0,
        "features": {
            "practice_interviews": {
                "name": "Practice Interviews",
                "description": "Limited access to practice interviews",
                "included": True
            },
            "ai_feedback": {
                "name": "AI Feedback",
                "description": "Basic AI feedback on your answers",
                "included": True
            },
            "interview_history": {
                "name": "Interview History",
                "description": "Access to your last 5 interviews",
                "included": True
            },
            "premium_questions": {
                "name": "Premium Question Bank",
                "description": "Access to premium interview questions",
                "included": False
            },
            "analytics": {
                "name": "Advanced Analytics",
                "description": "Detailed performance analytics",
                "included": False
            }
        },
        "limits": {
            "max_interviews": 5,
            "max_questions_per_interview": 5,
            "max_storage_gb": 0.5,
            "max_audio_length_mins": 15
        },
        "is_ai_feedback_enabled": True,
        "is_export_enabled": False,
        "is_premium_questions_enabled": False,
        "sort_order": 1,
        "is_public": True
    },
    {
        "name": "Basic",
        "code": "basic",
        "description": "Enhanced interview preparation for serious candidates",
        "price_monthly": 9.99,
        "price_yearly": 99.99,  # ~16% discount
        "currency": "USD",
        "trial_days": 7,
        "setup_fee": 0.0,
        "features": {
            "practice_interviews": {
                "name": "Practice Interviews",
                "description": "Unlimited access to practice interviews",
                "included": True
            },
            "ai_feedback": {
                "name": "AI Feedback",
                "description": "Detailed AI feedback on your answers",
                "included": True
            },
            "interview_history": {
                "name": "Interview History",
                "description": "Access to your full interview history",
                "included": True
            },
            "premium_questions": {
                "name": "Premium Question Bank",
                "description": "Access to premium interview questions",
                "included": True
            },
            "analytics": {
                "name": "Advanced Analytics",
                "description": "Detailed performance analytics",
                "included": False
            }
        },
        "limits": {
            "max_interviews": 20,
            "max_questions_per_interview": 10,
            "max_storage_gb": 2.0,
            "max_audio_length_mins": 30
        },
        "is_ai_feedback_enabled": True,
        "is_export_enabled": True,
        "is_premium_questions_enabled": True,
        "sort_order": 2,
        "is_public": True,
        "highlight": True
    },
    {
        "name": "Premium",
        "code": "premium",
        "description": "Comprehensive interview preparation platform",
        "price_monthly": 19.99,
        "price_yearly": 191.99,  # ~20% discount
        "currency": "USD",
        "trial_days": 7,
        "setup_fee": 0.0,
        "features": {
            "practice_interviews": {
                "name": "Practice Interviews",
                "description": "Unlimited access to practice interviews",
                "included": True
            },
            "ai_feedback": {
                "name": "AI Feedback",
                "description": "Advanced AI feedback with improvement suggestions",
                "included": True
            },
            "interview_history": {
                "name": "Interview History",
                "description": "Access to your full interview history",
                "included": True
            },
            "premium_questions": {
                "name": "Premium Question Bank",
                "description": "Access to premium interview questions",
                "included": True
            },
            "analytics": {
                "name": "Advanced Analytics",
                "description": "Detailed performance analytics",
                "included": True
            },
            "expert_review": {
                "name": "Expert Review",
                "description": "Monthly expert review of your interviews",
                "included": True
            }
        },
        "limits": {
            "max_interviews": None,  # Unlimited
            "max_questions_per_interview": None,  # Unlimited
            "max_storage_gb": 10.0,
            "max_audio_length_mins": 60
        },
        "is_ai_feedback_enabled": True,
        "is_export_enabled": True,
        "is_premium_questions_enabled": True,
        "is_custom_branding_enabled": True,
        "sort_order": 3,
        "is_public": True
    }
]


def sync_stripe_products_and_prices(db: Session) -> Dict[str, Dict[str, str]]:
    """
    Sync subscription plans with Stripe products and prices.
    Returns a mapping of plan codes to Stripe IDs.
    """
    # Get existing subscription plans from the database
    db_plans = db.query(SubscriptionPlan).all()
    product_map = {}
    
    # Get or create the main product
    main_product = db.query(Product).filter(Product.code == "interview_prep").first()
    if not main_product:
        # Create the product in database
        main_product = Product(
            name="Interview Prep Platform",
            code="interview_prep",
            description="Comprehensive interview preparation platform"
        )
        db.add(main_product)
        db.commit()
        db.refresh(main_product)
        
        # Create the product in Stripe
        stripe_product = create_product(
            name="Interview Prep Platform",
            description="Comprehensive interview preparation platform",
            metadata={"product_id": main_product.id}
        )
        
        # Update the Stripe product ID in the database
        main_product.stripe_product_id = stripe_product.id
        db.add(main_product)
        db.commit()
        db.refresh(main_product)
    
    for plan_data in SUBSCRIPTION_PLANS:
        code = plan_data["code"]
        product_map[code] = {"product_id": main_product.stripe_product_id}
        
        # Find existing plan in database
        db_plan = next((p for p in db_plans if p.code == code), None)
        
        # If plan doesn't exist, create it
        if not db_plan:
            # Create plan in database first
            db_plan = SubscriptionPlan(
                name=plan_data["name"],
                code=code,
                description=plan_data["description"],
                price_monthly=plan_data["price_monthly"],
                price_yearly=plan_data.get("price_yearly"),
                currency=plan_data["currency"],
                trial_days=plan_data.get("trial_days", 0),
                setup_fee=plan_data.get("setup_fee", 0.0),
                max_interviews=plan_data.get("limits", {}).get("max_interviews"),
                max_questions_per_interview=plan_data.get("limits", {}).get("max_questions_per_interview"),
                max_storage_gb=plan_data.get("limits", {}).get("max_storage_gb"),
                max_audio_length_mins=plan_data.get("limits", {}).get("max_audio_length_mins"),
                features=plan_data.get("features"),
                is_ai_feedback_enabled=plan_data.get("is_ai_feedback_enabled", False),
                is_export_enabled=plan_data.get("is_export_enabled", False),
                is_team_access_enabled=plan_data.get("is_team_access_enabled", False),
                is_premium_questions_enabled=plan_data.get("is_premium_questions_enabled", False),
                is_custom_branding_enabled=plan_data.get("is_custom_branding_enabled", False),
                is_public=plan_data.get("is_public", True),
                is_active=plan_data.get("is_active", True),
                highlight=plan_data.get("highlight", False),
                sort_order=plan_data.get("sort_order", 0),
                product_id=main_product.id
            )
            db.add(db_plan)
            db.commit()
            db.refresh(db_plan)
        
        # Skip creating Stripe prices for the free plan
        if code == "free" or plan_data["price_monthly"] == 0:
            continue
        
        # Create or update Stripe prices
        if not db_plan.stripe_price_id:
            # Convert dollars to cents for Stripe
            monthly_price_cents = int(plan_data["price_monthly"] * 100)
            yearly_price_cents = int(plan_data.get("price_yearly", 0) * 100)
            
            # Create monthly price in Stripe
            monthly_price = create_price(
                product_id=main_product.stripe_product_id,
                unit_amount=monthly_price_cents,
                currency=plan_data["currency"].lower(),
                recurring={"interval": "month"},
                metadata={"plan_id": db_plan.id, "interval": "month"}
            )
            
            # Update monthly price ID in database
            db_plan.stripe_price_id = monthly_price.id
            product_map[code]["price_monthly"] = monthly_price.id
            
            # Create yearly price if applicable
            if yearly_price_cents > 0:
                yearly_price = create_price(
                    product_id=main_product.stripe_product_id,
                    unit_amount=yearly_price_cents,
                    currency=plan_data["currency"].lower(),
                    recurring={"interval": "year"},
                    metadata={"plan_id": db_plan.id, "interval": "year"}
                )
                product_map[code]["price_yearly"] = yearly_price.id
                
                # Store yearly price ID in metadata
                if not db_plan.features:
                    db_plan.features = {}
                
                features = db_plan.features
                if isinstance(features, dict):
                    features["stripe_yearly_price_id"] = yearly_price.id
                    db_plan.features = features
            
            # Update product ID and pricing in the database
            db_plan.stripe_product_id = main_product.stripe_product_id
            db.add(db_plan)
            db.commit()
            db.refresh(db_plan)
        else:
            # Add existing price IDs to the map
            product_map[code]["price_monthly"] = db_plan.stripe_price_id
            
            # Add yearly price if it exists
            if db_plan.features and isinstance(db_plan.features, dict) and "stripe_yearly_price_id" in db_plan.features:
                product_map[code]["price_yearly"] = db_plan.features["stripe_yearly_price_id"]
    
    return product_map


def get_subscription_plans_from_db(db: Session) -> List[SubscriptionPlan]:
    """
    Get all public subscription plans from the database, ordered by sort_order.
    """
    return (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.is_public == True, SubscriptionPlan.is_active == True)
        .order_by(SubscriptionPlan.sort_order)
        .all()
    )


def get_plan_by_code(db: Session, code: str) -> Optional[SubscriptionPlan]:
    """
    Get a subscription plan by its code.
    """
    return (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.code == code, SubscriptionPlan.is_active == True)
        .first()
    )


def get_plan_details(plan: SubscriptionPlan, billing_cycle: str = "monthly") -> PlanDetails:
    """
    Convert a SubscriptionPlan model to a PlanDetails schema for the API.
    """
    # Determine which price to use based on billing cycle
    price = plan.price_yearly if billing_cycle == "yearly" and plan.price_yearly else plan.price_monthly
    
    # Extract features
    plan_features = []
    if plan.features and isinstance(plan.features, dict):
        for feature_id, feature_data in plan.features.items():
            # Skip non-feature keys like stripe_yearly_price_id
            if not isinstance(feature_data, dict):
                continue
                
            if "name" in feature_data and "included" in feature_data:
                plan_features.append(
                    PlanFeature(
                        name=feature_data["name"],
                        description=feature_data.get("description", ""),
                        included=feature_data["included"]
                    )
                )
    
    # Create a PlanDetails object
    return PlanDetails(
        id=plan.code,
        name=plan.name,
        description=plan.description,
        price=price,
        currency=plan.currency.lower(),
        interval=billing_cycle,
        features=plan_features,
        popular=plan.highlight,
        trial_days=plan.trial_days
    )


def get_formatted_plans(db: Session, billing_cycle: str = "monthly") -> List[PlanDetails]:
    """
    Get formatted subscription plans for the API.
    """
    db_plans = get_subscription_plans_from_db(db)
    return [get_plan_details(plan, billing_cycle) for plan in db_plans]


def get_stripe_price_id(plan: SubscriptionPlan, billing_cycle: str = "monthly") -> Optional[str]:
    """
    Get the Stripe price ID for a plan based on the billing cycle.
    """
    # Monthly price is stored directly in the stripe_price_id field
    if billing_cycle == "monthly":
        return plan.stripe_price_id
    
    # Yearly price is stored in the features JSON field
    if billing_cycle == "yearly" and plan.features and isinstance(plan.features, dict):
        return plan.features.get("stripe_yearly_price_id")
    
    return None
