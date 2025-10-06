from flask import Blueprint, jsonify
from src.middleware.auth import jwt_required, admin_required, optional_auth
from src.middleware.utils import rate_limit, validate_json

users_blueprint = Blueprint("users", __name__)

@users_blueprint.route("/", methods=['GET'])
@rate_limit(max_requests=50, window_seconds=3600)  # 50 requests per hour
@optional_auth  # Authentication is optional for this endpoint
def getAllUsers(current_user=None):
    """Get all users - authentication optional"""
    if current_user:
        return jsonify({
            "message": f"Hello {current_user.email}, here are all users",
            "users": []
        })
    else:
        return jsonify({
            "message": "Here are all users (public view)",
            "users": []
        })

@users_blueprint.route("/<user_id>", methods=['GET'])
@jwt_required
def getUser(current_user, user_id):
    """Get specific user - authentication required"""
    return jsonify({
        "message": f"User {user_id} details",
        "requested_by": current_user.email
    })

@users_blueprint.route("/<user_id>", methods=['PUT'])
@validate_json
@jwt_required
def editUser(current_user, user_id):
    """Edit user - authentication required + JSON validation"""
    return jsonify({
        "message": f"User {user_id} updated by {current_user.email}"
    })

@users_blueprint.route("/<user_id>", methods=['DELETE'])
@admin_required  # Only admins can delete users
def deleteUser(current_user, user_id):
    """Delete user - admin privileges required"""
    return jsonify({
        "message": f"User {user_id} deleted by admin {current_user.email}"
    })

