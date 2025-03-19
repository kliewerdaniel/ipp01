from fastapi import APIRouter, Request, Response, Depends, HTTPException
from sqlalchemy.orm import Session
import stripe
import json
import logging

from app.db.session import get_db
from app.core.config import settings
from app.services.subscription import process_subscription_updated, process_subscription_deleted
from app.services.payment import process_payment_succeeded, process_payment_failed
from app.models.billing_history import BillingEventType
from app.schemas.payment import WebhookPayloadResponse

# Initialize router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/stripe", response_model=WebhookPayloadResponse)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events.
    
    This endpoint receives webhook events from Stripe and processes them
    based on the event type. It handles subscription creations, updates,
    cancellations, and payment events.
    """
    # Get the raw payload
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid Stripe webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid Stripe signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Extract the event type and data
    event_type = event["type"]
    data = event["data"]["object"]
    
    # Log the event for debugging
    logger.info(f"Received Stripe webhook: {event_type}")
    logger.debug(f"Event data: {json.dumps(data)}")
    
    # Process different event types
    try:
        if event_type.startswith("customer.subscription"):
            # Handle subscription events
            if event_type == "customer.subscription.created":
                # Subscription created (usually handled by our own API already)
                logger.info(f"Subscription created: {data['id']}")
                
            elif event_type == "customer.subscription.updated":
                # Subscription updated
                process_subscription_updated(db, data)
                
            elif event_type == "customer.subscription.deleted":
                # Subscription canceled
                process_subscription_deleted(db, data)
                
            elif event_type == "customer.subscription.trial_will_end":
                # Trial ending soon (usually 3 days before)
                # This is a good place to notify the user
                customer_id = data.get("customer")
                trial_end = data.get("trial_end")
                logger.info(f"Trial ending soon for customer {customer_id}. Trial ends at {trial_end}")
                # You can add notification logic here
        
        elif event_type.startswith("invoice"):
            # Handle invoice events
            if event_type == "invoice.payment_succeeded":
                # Payment succeeded
                process_payment_succeeded(db, data)
                
            elif event_type == "invoice.payment_failed":
                # Payment failed
                process_payment_failed(db, data)
                
            elif event_type == "invoice.finalized":
                # Invoice finalized, ready to be paid
                logger.info(f"Invoice finalized: {data['id']} for customer {data.get('customer')}")
                
        elif event_type.startswith("charge"):
            # Handle charge events (if needed)
            if event_type == "charge.succeeded":
                logger.info(f"Charge succeeded: {data['id']} for {data.get('amount')/100} {data.get('currency')}")
                
            elif event_type == "charge.failed":
                logger.info(f"Charge failed: {data['id']}, reason: {data.get('failure_message')}")
                
        # Add more event types as needed
                
        return WebhookPayloadResponse(
            received=True,
            event_type=event_type,
            details={"id": event["id"]}
        )
        
    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {str(e)}", exc_info=True)
        # We return a 200 response even on processing error so Stripe doesn't retry
        # But we log the error for investigation
        return WebhookPayloadResponse(
            received=True,
            event_type=event_type,
            details={"error": str(e)}
        )


@router.post("/other-payment-provider")
async def other_payment_webhook(request: Request):
    """
    Placeholder for other payment provider webhooks.
    
    If you plan to support multiple payment providers, you can 
    add additional webhook handlers as needed.
    """
    payload = await request.json()
    logger.info(f"Received webhook from other payment provider: {payload}")
    return {"received": True}
