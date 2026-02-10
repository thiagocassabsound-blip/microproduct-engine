import traceback
import time
try:
    from execucao.utils import setup_logger
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger

logger = setup_logger('Guardian')

class Guardian:
    def __init__(self):
        self.error_log = []

    def watch(self, task_func, *args, **kwargs):
        """
        Executes a task safely. If it fails, logs logic and retries once.
        """
        try:
            return task_func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            stack = traceback.format_exc()
            logger.error(f"Guardian detected failure in {task_func.__name__}: {error_msg}")
            
            self.error_log.append({
                "timestamp": time.time(),
                "function": task_func.__name__,
                "error": error_msg,
                "stack": stack
            })
            
            # Simple self-correction: Wait and Retry
            logger.info("Attempting self-correction (Wait 5s and Retry)...")
            time.sleep(5)
            
            try:
                return task_func(*args, **kwargs)
            except Exception as retry_e:
                logger.critical(f"Retry failed for {task_func.__name__}: {retry_e}")
                return None

    def diagnose(self):
        """
        Returns a summary of errors.
        """
        return self.error_log
