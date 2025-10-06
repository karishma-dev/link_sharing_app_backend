from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError, EmailStr
from src.models.models import User, db
from src.middleware.auth import jwt_required

auth_blueprint = Blueprint('auth', __name__)

class Signup(BaseModel):
    email: EmailStr
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

@auth_blueprint.route("/login", methods=['POST'])
def login():
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        # Validate data using Pydantic model
        login_data = Login(**data)
        
        # Find user by email
        user = User.query.filter_by(email=login_data.email).first()
        
        if not user:
            return jsonify({
                "error": "Invalid email or password"
            }), 401
        
        # Check password
        if not user.check_password(login_data.password):
            return jsonify({
                "error": "Invalid email or password"
            }), 401
        
        # Generate JWT token
        token = user.generate_token()
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "firstName": user.firstName,
                "lastName": user.lastName
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation failed",
            "details": e.errors()
        }), 400
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            "error": "Login failed"
        }), 500

@auth_blueprint.route("/signup", methods=['POST'])
def signup():
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        # Validate data using Pydantic model
        user_data = Signup(**data)
        
        # Check if user already exists - Look how simple this is now!
        try:
            existing_user = User.query.filter_by(email=user_data.email).first()
            print(f"Database query result: {existing_user}")  # Debug log
        except Exception as db_error:
            print(f"Database error: {db_error}")  # Debug log
            return jsonify({
                "error": "Database connection error"
            }), 500
        
        if existing_user:
            return jsonify({
                "error": "User with this email already exists"
            }), 409
        
        # Create new user - Also super simple!
        try:
            new_user = User(
                email=user_data.email
            )
            # Hash the password before storing
            new_user.set_password(user_data.password)
            
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                "message": "User registered successfully",
                "user": {
                    "id": str(new_user.id),
                    "email": new_user.email
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {e}")
            return jsonify({
                "error": "Failed to create user"
            }), 500
        
    except ValidationError as e:
        # Return validation errors
        return jsonify({
            "error": "Validation failed",
            "details": e.errors()
        }), 400
    except Exception as e:
        # Handle other errors
        print(f"Unexpected error: {e}")  # Debug log
        return jsonify({
            "error": "Internal server error"
        }), 500

# @auth_blueprint.route("/verify-email-signup", methods=['POST'])
# def verifyEmailSignup():
#     return jsonify({"message": "Verify email signup endpoint"}), 200

@auth_blueprint.route("/forgot-password", methods=['POST'])
def forgotPassword():
    return jsonify({"message": "Forgot password endpoint"}), 200

@auth_blueprint.route("/reset-password", methods=['POST'])
def resetPassword():
    return jsonify({"message": "Reset password endpoint"}), 200

@auth_blueprint.route("/change-password", methods=['POST'])
def changePassword():
    return jsonify({"message": "Change password endpoint"}), 200

@auth_blueprint.route("/profile", methods=['GET'])
@jwt_required
def get_profile(current_user):
    """Protected route example - requires JWT token"""
    return jsonify({
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "firstName": current_user.firstName,
            "lastName": current_user.lastName,
            "image": current_user.image,
            "links": current_user.links
        }
    }), 200
