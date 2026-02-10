import os
import json
import time
try:
    from execucao.utils import setup_logger
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger

logger = setup_logger('TelemetryTracker')

class TelemetryTracker:
    def __init__(self):
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'telemetria', 'data')
        os.makedirs(self.log_dir, exist_ok=True)
        self.events_file = os.path.join(self.log_dir, 'events.jsonl')

    def track_event(self, event_type, data):
        """
        Logs an event to the local file.
        """
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "data": data
        }
        
        try:
            with open(self.events_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
            logger.debug(f"Event tracked: {event_type}")
        except Exception as e:
            logger.error(f"Error tracking event: {e}")

    def get_metrics(self, product_id):
        """
        Calculates simple metrics from the logs.
        """
        visits = 0
        conversions = 0
        
        try:
            if not os.path.exists(self.events_file):
                return {"visits": 0, "conversions": 0, "conversion_rate": 0.0}

            with open(self.events_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        app_json = json.loads(line)
                        if app_json['data'].get('product_id') == product_id:
                            if app_json['type'] == 'visit':
                                visits += 1
                            elif app_json['type'] == 'checkout_complete':
                                conversions += 1
                    except:
                        continue
            
            rate = (conversions / visits) if visits > 0 else 0.0
            return {
                "visits": visits, 
                "conversions": conversions, 
                "conversion_rate": rate
            }
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}
