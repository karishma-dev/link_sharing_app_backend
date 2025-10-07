from flask import request, jsonify
from functools import wraps
from src.models.models import User
import uuid


def jwt_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Verify token
            payload = User.verify_token(token)
            if payload is None:
                return jsonify({'error': 'Token is invalid or expired'}), 401
            
            # Get current user - convert string UUID back to UUID object
            user_id_str = payload['user_id']
            try:
                user_uuid = uuid.UUID(user_id_str)
                current_user = User.query.filter_by(id=user_uuid).first()
            except ValueError:
                return jsonify({'error': 'Invalid user ID in token'}), 401
                
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
        except Exception as e:
            print(f"Token verification error: {e}")  # Debug log
            return jsonify({'error': 'Token verification failed'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to protect routes that require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # This would use jwt_required first, then check if user is admin
        # For now, it's just a placeholder - you can implement admin logic later
        return jwt_required(f)(*args, **kwargs)
    
    return decorated