# app/api/v1/endpoints/auth.py
from flask import request, Blueprint
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import user_db
import re

def validate_email(email):
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Password validation - at least 6 characters"""
    return len(password) >= 6

class RegisterAPI(Resource):
    def post(self):
        """Register a new user"""
        try:
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            # Validation
            if not username:
                return {"error": "Username is required"}, 400
            
            if not email:
                return {"error": "Email is required"}, 400
            
            if not password:
                return {"error": "Password is required"}, 400
            
            if not validate_email(email):
                return {"error": "Invalid email format"}, 400
            
            if not validate_password(password):
                return {"error": "Password must be at least 6 characters long"}, 400
            
            # Create user
            user = user_db.create_user(username, email, password)
            
            if not user:
                return {"error": "User with this username or email already exists"}, 409
            
            # Create access token - convert user ID to string
            access_token = create_access_token(identity=str(user.id))
            
            return {
                "message": "User registered successfully",
                "user": user.to_dict(),
                "access_token": access_token
            }, 201
            
        except Exception as e:
            return {"error": str(e)}, 500

class LoginAPI(Resource):
    def post(self):
        """Login user"""
        try:
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                return {"error": "Username and password are required"}, 400
            
            # Find user
            user = user_db.get_user_by_username(username)
            
            if not user:
                return {"error": "Invalid credentials"}, 401
            
            # Verify password
            if not user_db.verify_password(user, password):
                return {"error": "Invalid credentials"}, 401
            
            # Create access token - convert user ID to string
            access_token = create_access_token(identity=str(user.id))
            
            return {
                "message": "Login successful",
                "user": user.to_dict(),
                "access_token": access_token
            }, 200
            
        except Exception as e:
            return {"error": str(e)}, 500

class ProfileAPI(Resource):
    @jwt_required()
    def get(self):
        """Get current user profile"""
        try:
            # Convert JWT identity back to int
            current_user_id = int(get_jwt_identity())
            user = user_db.get_user_by_id(current_user_id)
            
            if not user:
                return {"error": "User not found"}, 404
            
            return {
                "user": user.to_dict()
            }, 200
            
        except Exception as e:
            return {"error": str(e)}, 500
    
    @jwt_required()
    def put(self):
        """Update current user profile"""
        try:
            current_user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            # Update user profile
            user = user_db.update_user_profile(current_user_id, **data)
            
            if not user:
                return {"error": "User not found"}, 404
            
            return {
                "message": "User profile updated successfully",
                "user": user.to_dict()
            }, 200
            
        except Exception as e:
            return {"error": str(e)}, 500


class LogoutAPI(Resource):
    @jwt_required()
    def post(self):
        """Logout user - client-side token removal instruction"""
        return {
            "message": "Logged out successfully. Please remove the token from your client storage."
        }, 200

class ProtectedAPI(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {"logged_in_as": current_user}, 200

auth_bp = Blueprint('auth_api', __name__)
api = Api(auth_bp)

# Add resources to the API
api.add_resource(RegisterAPI, '/register')
api.add_resource(LoginAPI, '/login')
api.add_resource(ProfileAPI, '/profile')
api.add_resource(LogoutAPI, '/logout')
api.add_resource(ProtectedAPI, '/protected')
