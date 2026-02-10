import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from execucao.utils import setup_logger, load_env_file
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger, load_env_file

logger = setup_logger('EmailAgent')
load_env_file()

class EmailAgent:
    def __init__(self):
        """
        Initialize Email Agent with Resend API.
        """
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('EMAIL_FROM', 'noreply@fastoolhub.com')
        self.log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'email_logs.jsonl')
        
        if not self.api_key:
            logger.warning("RESEND_API_KEY not found. Email sending will be mocked.")
            self.client = None
        else:
            try:
                import resend
                resend.api_key = self.api_key
                self.client = resend
                logger.info("Resend client initialized successfully.")
            except ImportError:
                logger.warning("Resend library not installed. Run: pip install resend")
                self.client = None
    
    def _load_template(self, template_name):
        """
        Load HTML template from email/templates/
        """
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'templates', 
            f'{template_name}.html'
        )
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Template {template_name}.html not found at {template_path}")
            return f"<html><body><h1>Email Template Missing</h1><p>Template: {template_name}</p></body></html>"
    
    def _log_email(self, recipient, subject, status, error=None):
        """
        Log email attempt to email_logs.jsonl
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'recipient': recipient,
            'subject': subject,
            'status': status,
            'error': error
        }
        
        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to log email: {e}")
    
    def retry_send(self, send_func, *args, max_retries=3, **kwargs):
        """
        Retry email sending with exponential backoff.
        """
        import time
        
        for attempt in range(max_retries):
            try:
                result = send_func(*args, **kwargs)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Email send attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(wait_time)
        
        logger.error(f"Email send failed after {max_retries} attempts")
        return False
    
    def send_product_delivery(self, email, product_info, download_link):
        """
        Send product delivery email with download link.
        
        Args:
            email: recipient email
            product_info: dict with 'name', 'description'
            download_link: secure download URL
        """
        logger.info(f"Sending product delivery email to {email}")
        
        template = self._load_template('delivery')
        html_content = template.replace('{{product_name}}', product_info.get('name', 'Your Product'))
        html_content = html_content.replace('{{product_description}}', product_info.get('description', ''))
        html_content = html_content.replace('{{download_link}}', download_link)
        
        subject = f"🎁 Your {product_info.get('name', 'Product')} is Ready!"
        
        if not self.client:
            logger.warning("MOCK: Product delivery email not sent (Resend not configured)")
            self._log_email(email, subject, 'mock')
            return True  # Mock success
        
        try:
            response = self.client.Emails.send({
                "from": self.from_email,
                "to": email,
                "subject": subject,
                "html": html_content
            })
            
            self._log_email(email, subject, 'sent')
            logger.info(f"Product delivery email sent successfully. ID: {response.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send product delivery email: {e}")
            self._log_email(email, subject, 'failed', str(e))
            return False
    
    def send_payment_confirmation(self, email, order_info):
        """
        Send payment confirmation email.
        
        Args:
            email: recipient email
            order_info: dict with 'product_name', 'amount', 'order_id'
        """
        logger.info(f"Sending payment confirmation to {email}")
        
        template = self._load_template('confirmation')
        html_content = template.replace('{{product_name}}', order_info.get('product_name', 'Product'))
        html_content = html_content.replace('{{amount}}', f"${order_info.get('amount', '0.00')}")
        html_content = html_content.replace('{{order_id}}', order_info.get('order_id', 'N/A'))
        
        subject = f"✅ Payment Confirmed - {order_info.get('product_name', 'Order')}"
        
        if not self.client:
            logger.warning("MOCK: Payment confirmation email not sent (Resend not configured)")
            self._log_email(email, subject, 'mock')
            return True
        
        try:
            response = self.client.Emails.send({
                "from": self.from_email,
                "to": email,
                "subject": subject,
                "html": html_content
            })
            
            self._log_email(email, subject, 'sent')
            logger.info(f"Payment confirmation sent successfully. ID: {response.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send payment confirmation: {e}")
            self._log_email(email, subject, 'failed', str(e))
            return False
    
    def send_feedback_request(self, email, product_name):
        """
        Send feedback request email (scheduled for later).
        
        Args:
            email: recipient email
            product_name: name of the product
        """
        logger.info(f"Sending feedback request to {email}")
        
        template = self._load_template('feedback')
        html_content = template.replace('{{product_name}}', product_name)
        
        subject = f"💬 How was {product_name}? We'd love your feedback!"
        
        if not self.client:
            logger.warning("MOCK: Feedback request email not sent (Resend not configured)")
            self._log_email(email, subject, 'mock')
            return True
        
        try:
            response = self.client.Emails.send({
                "from": self.from_email,
                "to": email,
                "subject": subject,
                "html": html_content
            })
            
            self._log_email(email, subject, 'sent')
            logger.info(f"Feedback request sent successfully. ID: {response.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send feedback request: {e}")
            self._log_email(email, subject, 'failed', str(e))
            return False


if __name__ == "__main__":
    # Test the email agent
    agent = EmailAgent()
    
    # Test product delivery
    test_product = {
        'name': 'Productivity Checklist',
        'description': 'A comprehensive checklist to boost your productivity'
    }
    agent.send_product_delivery('test@example.com', test_product, 'https://example.com/download/abc123')
