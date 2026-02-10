try:
    from execucao.utils import setup_logger
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger

logger = setup_logger('ProductValidator')

class ProductValidator:
    def validate(self, filepath, product_type):
        """
        Basic validation of the generated file.
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return False

        size = os.path.getsize(filepath)
        if size == 0:
            logger.error(f"File is empty: {filepath}")
            return False

        # Could add specific checks per type (e.g. check for syntax errors in .py)
        logger.info(f"Product validated: {filepath} ({size} bytes)")
        return True
