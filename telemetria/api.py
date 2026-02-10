import os
import sys
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from execucao.utils import setup_logger
except ImportError:
    from execucao.utils import setup_logger

logger = setup_logger('TelemetryAPI')

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# File to store telemetry events
EVENTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'events.jsonl')

def save_event(event_data):
    """Save event to events.jsonl"""
    try:
        os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
        with open(EVENTS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event_data) + '\n')
        return True
    except Exception as e:
        logger.error(f"Failed to save event: {e}")
        return False

@app.route('/api/track', methods=['POST', 'OPTIONS'])
def track_event():
    """
    Telemetry API endpoint to receive frontend events.
    
    Expected payload:
    {
        "type": "visit" | "cta_click" | "checkout_start" | "product_usage" | "refund",
        "product_id": "optional_product_slug",
        "metadata": {additional_context}
    }
    """
    if request.method == 'OPTIONS':
        # Handle preflight CORS request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 200
    
    try:
        data = request.get_json()
        
        if not data or 'type' not in data:
            return jsonify({'error': 'Missing required field: type'}), 400
        
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': data.get('type'),
            'product_id': data.get('product_id', 'unknown'),
            'metadata': data.get('metadata', {}),
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        if save_event(event):
            logger.info(f"Event tracked: {event['type']} for product {event['product_id']}")
            return jsonify({'status': 'success', 'event_id': event['timestamp']}), 200
        else:
            return jsonify({'error': 'Failed to save event'}), 500
            
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'service': 'telemetry-api'}), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'FastoolHub Telemetry API',
        'version': '1.0.0',
        'endpoints': {
            '/api/track': 'POST - Track telemetry events',
            '/health': 'GET - Health check'
        }
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting Telemetry API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
