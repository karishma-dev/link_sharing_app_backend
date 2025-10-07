from flask import request, jsonify
import time
from functools import wraps

def validate_json(f):
    """Middleware to ensure request contains valid JSON"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        try:
            request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        return f(*args, **kwargs)
    
    return decorated


def cors_headers(f):
    """Add CORS headers to response"""
    @wraps(f)
    def decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # If response is a tuple (data, status_code), handle it
        if isinstance(response, tuple):
            data, status_code = response
            response = jsonify(data) if not hasattr(data, 'headers') else data
            response.status_code = status_code
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    return decorated