"""
Database models package initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# Import models to make them available when importing from app.models
from app.models.user import User
from app.models.anomaly import Anomaly
from app.models.maintenance import MaintenanceWindow
from app.models.action_plan import ActionPlan, ActionItem
from app.models.database import user_db
