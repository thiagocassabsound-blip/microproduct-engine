try:
    from execucao.utils import setup_logger
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger

logger = setup_logger('UpgradeLoop')

class UpgradeManager:
    def check_for_upgrade(self, product_id, feedback_list):
        """
        Determines if a product needs an upgrade.
        """
        negative_feedback = [f for f in feedback_list if f.get('sentiment') == 'negative']
        
        if len(negative_feedback) > 3:
            logger.info(f"Product {product_id} has negative feedback. Triggering upgrade.")
            return True, "Improve content based on negative feedback."
        
        return False, ""
