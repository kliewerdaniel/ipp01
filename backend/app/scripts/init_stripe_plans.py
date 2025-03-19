import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path to allow imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    sys.path.insert(0, os.path.dirname(parent_dir))  # Add project root

from app.db.session import SessionLocal
from app.services.subscription_plan_service import sync_stripe_products_and_prices
from app.core.config import settings


if __name__ == "__main__":
    """
    Initialize Stripe subscription plans in both the database and Stripe.
    
    Usage: python init_stripe_plans.py
    
    Before running:
    1. Make sure your Stripe API key is set in environment variables or .env file
    2. This will create or update plans in both your database and Stripe
    """
    
    if not settings.STRIPE_API_KEY:
        logger.error("STRIPE_API_KEY not configured. Please set it before running this script.")
        sys.exit(1)
    
    logger.info("Starting Stripe plan synchronization...")
    
    try:
        # Get database session
        db = SessionLocal()
        
        # Sync plans with Stripe
        plan_mapping = sync_stripe_products_and_prices(db)
        
        logger.info(f"Successfully synchronized plans with Stripe")
        logger.info(f"Plan mapping: {plan_mapping}")
        
        # Close session
        db.close()
        
    except Exception as e:
        logger.error(f"Error syncing plans with Stripe: {str(e)}")
        sys.exit(1)
    
    logger.info("Stripe plan initialization complete")
