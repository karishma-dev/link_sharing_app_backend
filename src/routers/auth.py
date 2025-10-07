from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError, EmailStr
from src.models.models import User, db, UserLink
from src.middleware.auth import jwt_required

auth_blueprint = Blueprint('auth', __name__)

class Signup(BaseModel):
    email: EmailStr
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

class ChangePassword(BaseModel):
    oldPassword: str
    newPassword: str

class UpdateProfile(BaseModel):
    firstName: str = None
    lastName: str = None
    image: str = None
    links: list = None  # List of {"platform_id": "uuid", "url": "string"}

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
            "user": user.to_dict()
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
                "user": new_user.to_dict()
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

@auth_blueprint.route("/forgot-password", methods=['POST'])
def forgotPassword():
    return jsonify({"message": "Forgot password endpoint"}), 200

@auth_blueprint.route("/reset-password", methods=['POST'])
def resetPassword():
    return jsonify({"message": "Reset password endpoint"}), 200

@auth_blueprint.route("/change-password", methods=['POST'])
@jwt_required
def changePassword(current_user):
    try:
        data = request.get_json()

        password_data = ChangePassword(**data)

        if not current_user.check_password(password_data.oldPassword):
            return jsonify({
                "error": "Invalid password"
            }), 401
        
        # Method 1: Direct attribute assignment (simplest)
        current_user.set_password(password_data.newPassword)
        
        # Save to database
        db.session.commit()
        
        return jsonify({
            "message": "Password changed successfully"
        }), 200
    except ValidationError as e:
        return jsonify({
            "error": "Validation failed",
            "details": e.errors()
        }), 400
    except Exception as e:
        print(f"Change Password error: {e}")
        return jsonify({
            "error": "Change Password failed"
        }), 500

@auth_blueprint.route("/profile", methods=['PUT'])
@jwt_required
def update_profile(current_user):
    """Update user profile information"""
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        # Validate data using Pydantic model
        profile_data = UpdateProfile(**data)
        
        # Method 2: Update multiple fields at once
        # Only update fields that were provided (not None) 
        
        if profile_data.firstName is not None:
            current_user.firstName = profile_data.firstName
            
        if profile_data.lastName is not None:
            current_user.lastName = profile_data.lastName
            
        if profile_data.image is not None:
            current_user.image = profile_data.image

        if profile_data.links is not None:
            # Delete existing links for this user
            UserLink.query.filter_by(user_id=current_user.id).delete()
            
            # Add new links
            for link_data in profile_data.links:
                if 'platform_id' in link_data and 'url' in link_data:
                    new_link = UserLink(
                        user_id=current_user.id,
                        platform_id=link_data['platform_id'],
                        url=link_data['url']
                    )
                    db.session.add(new_link)

        # Save to database
        db.session.commit()
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": current_user.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Validation failed",
            "details": e.errors()
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"Update profile error: {e}")
        return jsonify({
            "error": "Profile update failed"
        }), 500

@auth_blueprint.route("/profile", methods=['GET'])
@jwt_required
def get_profile(current_user):
    return jsonify({
        "user": current_user.to_dict()
    }), 200


# SQLAlchemy Update Methods:
# 1. Direct attribute assignment: user.name = "New Name"
# 2. update() method: User.query.filter_by(id=user_id).update({"name": "New Name"})
# 3. Bulk updates: User.query.filter(condition).update({"field": "value"})
# 4. Using session.merge() for detached objects


# Additional SQLAlchemy Update Examples:
#
# Method 3: Using update() method (good for bulk updates)
# User.query.filter_by(id=user_id).update({"firstName": "John", "lastName": "Doe"})
#
# Method 4: Bulk update multiple records
# User.query.filter(User.email.like('%@example.com')).update({"image": "default.jpg"})
#
# Method 5: Using session.merge() for detached objects
# user = User(id=user_id, firstName="John")  # Detached object
# db.session.merge(user)  # Updates existing or creates new
#
# Method 6: Update with conditions
# User.query.filter(User.created_at < datetime.now() - timedelta(days=30)).update({"status": "inactive"})
#
# Method 7: Update without loading object (efficient for single field)
# User.query.filter_by(id=user_id).update({"lastLogin": datetime.now()})
# db.session.commit()

# Example: When to use update() vs direct assignment
#
# Use update() when:
# - You only need to update 1-2 fields and don't need the object data
# - Bulk updates (updating many records at once)
# - Performance critical (avoids loading object into memory)
#
# Use direct assignment when:
# - You already have the object loaded (like from JWT middleware)
# - You need to access object data after update
# - You want to validate data before saving
# - Complex business logic that needs the full object
