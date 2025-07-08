"""
API v1 package initialization
"""

from flask import Blueprint
from .endpoints.auth import auth_bp
from .endpoints.anomalies import anomalies_bp
# Import other endpoint blueprints here
# from .endpoints.some_other_endpoint import some_other_bp

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/v1')

# Register the individual endpoint blueprints
api_v1_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_v1_bp.register_blueprint(anomalies_bp, url_prefix='/anomalies')
# Register other blueprints here
# api_v1_bp.register_blueprint(some_other_bp, url_prefix='/some_other')
