"""
TAMS - Technical Asset Management System Flask Application
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_migrate import Migrate
from flasgger import Swagger
import os

from app.models import db, bcrypt
from app.core.browsable_api import BrowsableAPI
from .api.v1.endpoints.auth import auth_bp
from .api.v1 import api_v1_bp  # Correctly import the blueprint
from .core.error_handlers import register_error_handlers
from .core.event_listeners import register_event_listeners

def create_app(config=None):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'taqathon-secret-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', os.environ.get('DATABASE_URI', 'sqlite:///tams.db')),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production'),
        JWT_ACCESS_TOKEN_EXPIRES=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400)),
        JWT_TOKEN_LOCATION=['headers'],
        SESSION_USE_SIGNER=True
    )
    
    # Override with custom config if provided
    if config:
        app.config.from_mapping(config)
    
    # Setup CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    
    # Register event listeners for automatic indexing
    register_event_listeners(app)

    # Initialize Swagger
    Swagger(app)
    
    # Register error handlers
    register_error_handlers(app)

    # Create a flask-restful API object for the browsable API only
    # We'll use this for documentation, but not for registering resources
    docs_api = Api(app)
    
    # Initialize browsable API with the docs_api
    browsable = BrowsableAPI(app, docs_api)
    
    # Register only the main API v1 Blueprint (which includes all sub-blueprints)
    app.register_blueprint(api_v1_bp, url_prefix='/api')

    # Register CLI commands
    from scripts.index_database import index_database_command
    app.cli.add_command(index_database_command)

    return app
