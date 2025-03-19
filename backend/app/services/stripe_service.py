import stripe
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Stripe client
if settings.STRIPE_API_KEY:
    stripe.api_key = settings.STRIPE_API_KEY
    logger.info("Stripe API initialized")
else:
    logger.warning("Stripe API key not configured. Stripe functionality will be limited.")

# Stripe webhook secret
webhook_secret = settings.STRIPE_WEBHOOK_SECRET


def construct_event(payload, sig_header):
    """
    Construct a Stripe event from webhook payload.
    """
    try:
        if not webhook_secret:
            logger.warning("Webhook secret not configured, skipping signature verification")
            return stripe.Event.construct_from(payload, stripe.api_key)
        
        return stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {str(e)}")
        raise
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {str(e)}")
        raise


def create_customer(email: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> stripe.Customer:
    """
    Create a new customer in Stripe.
    """
    try:
        return stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {}
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating customer: {str(e)}")
        raise


def get_or_create_customer(email: str, name: str, customer_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> stripe.Customer:
    """
    Get a customer by ID or create a new one if not found.
    """
    if customer_id:
        try:
            return stripe.Customer.retrieve(customer_id)
        except stripe.error.StripeError as e:
            logger.warning(f"Error retrieving customer {customer_id}: {str(e)}")
            # Fall through to create a new customer
    
    return create_customer(email, name, metadata)


def attach_payment_method(customer_id: str, payment_method_id: str) -> stripe.PaymentMethod:
    """
    Attach a payment method to a customer.
    """
    try:
        return stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error attaching payment method: {str(e)}")
        raise


def set_default_payment_method(customer_id: str, payment_method_id: str) -> stripe.Customer:
    """
    Set the default payment method for a customer.
    """
    try:
        return stripe.Customer.modify(
            customer_id,
            invoice_settings={
                'default_payment_method': payment_method_id
            }
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error setting default payment method: {str(e)}")
        raise


def create_product(name: str, description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> stripe.Product:
    """
    Create a new product in Stripe.
    """
    try:
        return stripe.Product.create(
            name=name,
            description=description,
            metadata=metadata or {}
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating product: {str(e)}")
        raise


def create_price(
    product_id: str, 
    unit_amount: int, 
    currency: str = 'usd',
    recurring: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> stripe.Price:
    """
    Create a new price for a product.
    """
    try:
        price_data = {
            'product': product_id,
            'unit_amount': unit_amount,
            'currency': currency,
            'metadata': metadata or {}
        }
        
        if recurring:
            price_data['recurring'] = recurring
        
        return stripe.Price.create(**price_data)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating price: {str(e)}")
        raise


def create_subscription(
    customer_id: str,
    price_id: str,
    trial_period_days: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    payment_behavior: str = 'default_incomplete',
    expand: Optional[List[str]] = None
) -> stripe.Subscription:
    """
    Create a new subscription for a customer.
    """
    try:
        subscription_data = {
            'customer': customer_id,
            'items': [{'price': price_id}],
            'payment_behavior': payment_behavior,
            'payment_settings': {'save_default_payment_method': 'on_subscription'},
            'metadata': metadata or {},
            'expand': expand or ['latest_invoice.payment_intent']
        }
        
        if trial_period_days:
            subscription_data['trial_period_days'] = trial_period_days
        
        return stripe.Subscription.create(**subscription_data)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating subscription: {str(e)}")
        raise


def update_subscription(
    subscription_id: str,
    price_id: Optional[str] = None,
    trial_period_days: Optional[int] = None,
    proration_behavior: Optional[str] = None,
    cancel_at_period_end: Optional[bool] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> stripe.Subscription:
    """
    Update an existing subscription.
    """
    try:
        update_data = {'metadata': metadata or {}}
        
        if price_id:
            update_data['items'] = [{'id': subscription_id, 'price': price_id}]
        
        if trial_period_days is not None:
            update_data['trial_period_days'] = trial_period_days
        
        if proration_behavior:
            update_data['proration_behavior'] = proration_behavior
        
        if cancel_at_period_end is not None:
            update_data['cancel_at_period_end'] = cancel_at_period_end
        
        return stripe.Subscription.modify(subscription_id, **update_data)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error updating subscription: {str(e)}")
        raise


def cancel_subscription(
    subscription_id: str,
    at_period_end: bool = True
) -> stripe.Subscription:
    """
    Cancel a subscription.
    """
    try:
        if at_period_end:
            return stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        else:
            return stripe.Subscription.delete(subscription_id)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error canceling subscription: {str(e)}")
        raise


def create_billing_portal_session(
    customer_id: str,
    return_url: str
) -> stripe.billing_portal.Session:
    """
    Create a billing portal session for a customer.
    """
    try:
        return stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating billing portal session: {str(e)}")
        raise


def create_checkout_session(
    customer_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
    trial_period_days: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> stripe.checkout.Session:
    """
    Create a checkout session for a subscription.
    """
    try:
        session_data = {
            'customer': customer_id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'mode': 'subscription',
            'line_items': [{'price': price_id, 'quantity': 1}],
            'metadata': metadata or {}
        }
        
        if trial_period_days:
            session_data['subscription_data'] = {
                'trial_period_days': trial_period_days
            }
        
        return stripe.checkout.Session.create(**session_data)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {str(e)}")
        raise


def retrieve_invoice(invoice_id: str) -> stripe.Invoice:
    """
    Retrieve an invoice by ID.
    """
    try:
        return stripe.Invoice.retrieve(invoice_id)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error retrieving invoice: {str(e)}")
        raise


def generate_invoice_pdf(invoice_id: str) -> str:
    """
    Generate a PDF for an invoice.
    """
    try:
        invoice = retrieve_invoice(invoice_id)
        return invoice.get('invoice_pdf', '')
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error generating invoice PDF: {str(e)}")
        raise
