import os
import stripe
try:
    from execucao.utils import setup_logger, load_env_file
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger, load_env_file

logger = setup_logger('StripeManager')
load_env_file()

class StripeManager:
    def __init__(self):
        self.api_key = os.getenv("PAYMENT_API_KEY")
        if self.api_key:
            stripe.api_key = self.api_key
        else:
            logger.warning("No PAYMENT_API_KEY found.")

    def create_payment_link(self, product_name, price_amount, description=""):
        """
        Creates a Stripe Product, Price, and Payment Link.
        Returns the URL.
        """
        if not self.api_key:
            logger.warning("Stripe Payment Key missing. Returning mock link.")
            return "#"

        try:
            # 1. Create Product
            product = stripe.Product.create(
                name=product_name,
                description=description
            )
            logger.info(f"Stripe Product created: {product.name}")

            # 2. Create Price (amount in cents)
            price = stripe.Price.create(
                unit_amount=int(price_amount * 100),
                currency="usd",
                product=product.id,
            )
            logger.info(f"Stripe Price created: ${price_amount}")

            # 3. Create Payment Link
            payment_link = stripe.PaymentLink.create(
                line_items=[{"price": price.id, "quantity": 1}],
                after_completion={"type": "redirect", "redirect": {"url": "http://fastoolhub.com/success"}} # Placeholder URL
            )
            
            logger.info(f"Payment Link created: {payment_link.url}")
            return payment_link.url

        except Exception as e:
            logger.error(f"Error creating Stripe payment link: {e}")
            return "#error"

if __name__ == "__main__":
    # Test
    sm = StripeManager()
    link = sm.create_payment_link("Test Product", 9.99, "Test Description")
    print(f"Test Link: {link}")
