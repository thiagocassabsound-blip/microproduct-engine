import logging
import os
import sys

def setup_logger(name=__name__, log_file='system.log', level=logging.INFO):
    """Function to setup as many loggers as you want"""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    handler = logging.FileHandler(os.path.join(log_dir, log_file))        
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    # Also log to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def load_env_file(filepath=None):
    """Load environment variables from a .env file using python-dotenv"""
    try:
        from dotenv import load_dotenv
        if filepath is None:
            filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        
        if os.path.exists(filepath):
            load_dotenv(filepath)
            return True
        return False
    except ImportError:
        # Fallback to manual parsing if dotenv is not installed
        if filepath is None:
            filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        
        if not os.path.exists(filepath):
            return False

        with open(filepath, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                    except ValueError:
                        continue
        return True
