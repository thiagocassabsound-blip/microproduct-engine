import os
import json
import sys
from flask import Flask, request, jsonify
import stripe

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from execucao.utils import setup_logger, load_env_file
except ImportError:
    from execucao.utils import setup_logger, load_env_file

try:
    from email.agent import EmailAgent
except ImportError:
    # Fallback if email module not found
    EmailAgent = None

logger = setup_logger('WebhookServer')
load_env_file()

app = Flask(__name__)

# Initialize Email Agent
email_agent = EmailAgent() if EmailAgent else None
if not email_agent:
    logger.warning("EmailAgent not available. Emails will not be sent.")

# Helper to find product file
def get_product_file(product_name):
    # This logic would need to be robust in a real app
    # For now, we assume product name maps to a file in temp/generated_products
    safe_name = product_name.lower().replace(' ', '_') + ".md"
    return safe_name

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('WEBHOOK_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error("Invalid payload")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid signature")
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Payment successful for session: {session.get('id')}")
        
        customer_email = session.get('customer_details', {}).get('email')
        amount_total = session.get('amount_total', 0) / 100  # Convert cents to dollars
        
        # Extract metadata (product name should be in line_items)
        # For now, use metadata or fallback
        metadata = session.get('metadata', {})
        product_name = metadata.get('product_name', 'Your Product')
        
        logger.info(f"Processing purchase: {product_name} for {customer_email}")
        
        if email_agent and customer_email:
            # 1. Send payment confirmation
            order_info = {
                'product_name': product_name,
                'amount': f"${amount_total:.2f}",
                'order_id': session.get('id')
            }
            email_agent.retry_send(
                email_agent.send_payment_confirmation,
                customer_email,
                order_info
            )
            
            # 2. Generate secure download link (mock for now)
            # In production, this would generate a signed URL with expiration
            product_slug = product_name.lower().replace(' ', '-')
            download_link = f"https://fastoolhub.com/download/{product_slug}-{session.get('id')[:8]}"
            
            # 3. Send product delivery email
            product_info = {
                'name': product_name,
                'description': metadata.get('product_description', 'Your digital product')
            }
            email_agent.retry_send(
                email_agent.send_product_delivery,
                customer_email,
                product_info,
                download_link
            )
            
            logger.info(f"✅ Product delivered to {customer_email}")
        else:
            logger.warning(f"Could not send email (email_agent: {bool(email_agent)}, email: {customer_email})")
        
        # Log delivery for tracking
        delivery_log = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'delivery_log.jsonl')
        os.makedirs(os.path.dirname(delivery_log), exist_ok=True)
        with open(delivery_log, "a") as f:
            log_entry = {
                'timestamp': session.get('created'),
                'session_id': session.get('id'),
                'customer_email': customer_email,
                'product_name': product_name,
                'amount': amount_total,
                'delivered': bool(email_agent)
            }
            f.write(json.dumps(log_entry) + '\n')

    return jsonify({'status': 'success'}), 200

@app.route('/success', methods=['GET'])
def success_page():
    return "<h1>Purchase Successful! Check your email for the product.</h1>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Webhook Server on port {port}")
    app.run(host='0.0.0.0', port=port)
