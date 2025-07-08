# database.py - Helper functions for database operations
from app.models import db
from app.models.user import User
from datetime import datetime

# Helper functions for backward compatibility and easier database operations
class UserDatabase:
    @staticmethod
    def create_user(username, email, password, name=None, role=None, department=None, phone=None):
        # Check if user already exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return None
        
        user = User(
            username=username, 
            email=email,
            name=name,
            role=role,
            department=department,
            phone=phone
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def verify_password(user, password):
        return user.check_password(password)
    
    @staticmethod
    def update_user_profile(user_id, **kwargs):
        """Update user profile with given fields"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        allowed_fields = ['name', 'role', 'department', 'phone', 'email']
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return user

# Global database instance for backward compatibility
user_db = UserDatabase()
