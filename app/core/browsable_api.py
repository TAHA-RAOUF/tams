"""
DRF-style browsable API for Flask
Provides a Django REST Framework-like interface for testing and browsing API endpoints
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_restful import Api
from functools import wraps
import inspect
import json
from datetime import datetime
import requests

browsable_api = Blueprint('browsable_api', __name__, template_folder='templates', static_folder='static')

class BrowsableAPI:
    def __init__(self, app=None, api=None):
        self.app = app
        self.api = api
        self.endpoints = {}
        
        if app:
            self.init_app(app, api)
    
    def init_app(self, app, api):
        self.app = app
        self.api = api
        
        # Register the blueprint
        app.register_blueprint(browsable_api, url_prefix='/api-browser')
        
        # Discover endpoints
        self._discover_endpoints()
        
        # Add context processor for templates
        @app.context_processor
        def inject_api_info():
            return {
                'api_title': 'TAQATHON Equipment Reliability API',
                'api_version': '1.0.0',
                'current_user': session.get('user'),
                'auth_token': session.get('auth_token')
            }
    
    def _discover_endpoints(self):
        """Discover all API endpoints and their metadata"""
        if not self.api:
            return
            
        for endpoint, view_func in self.api.app.view_functions.items():
            if endpoint.startswith('api.'):
                # Get the resource class
                resource_class = getattr(view_func, 'view_class', None)
                if resource_class:
                    self._extract_endpoint_info(endpoint, resource_class)
    
    def _extract_endpoint_info(self, endpoint, resource_class):
        """Extract information about an endpoint"""
        methods = []
        
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            if hasattr(resource_class, method.lower()):
                method_func = getattr(resource_class, method.lower())
                
                # Extract docstring and parameters
                doc = inspect.getdoc(method_func) or f"{method} {endpoint}"
                
                methods.append({
                    'method': method,
                    'description': doc,
                    'requires_auth': self._requires_auth(method_func),
                    'parameters': self._extract_parameters(method_func)
                })
        
        if methods:
            self.endpoints[endpoint] = {
                'path': endpoint.replace('api.', '/api/v1/'),
                'methods': methods,
                'resource_class': resource_class.__name__
            }
    
    def _requires_auth(self, func):
        """Check if a method requires authentication"""
        # Check for JWT decorators or auth requirements
        return hasattr(func, '__wrapped__') or 'jwt_required' in str(func)
    
    def _extract_parameters(self, func):
        """Extract parameters from function signature and docstring"""
        try:
            sig = inspect.signature(func)
            params = []
            
            for param_name, param in sig.parameters.items():
                if param_name not in ['self', 'args', 'kwargs']:
                    params.append({
                        'name': param_name,
                        'required': param.default == inspect.Parameter.empty,
                        'type': 'string'
                    })
            
            return params
        except:
            return []

# Routes for the browsable API
@browsable_api.route('/')
def index():
    """Main API browser page"""
    return render_template('api_browser/index.html')

# Helper function to get all endpoints info
def get_endpoints_info():
    """Get information about all API endpoints"""
    return {
        # Authentication endpoints
        '/api/v1/auth/register': {
            'methods': ['POST'],
            'description': 'Register a new user account',
            'requires_auth': False,
            'parameters': [
                {'name': 'username', 'type': 'string', 'required': True},
                {'name': 'email', 'type': 'string', 'required': True},
                {'name': 'password', 'type': 'string', 'required': True},
                {'name': 'name', 'type': 'string', 'required': False},
                {'name': 'role', 'type': 'string', 'required': False},
                {'name': 'department', 'type': 'string', 'required': False}
            ]
        },
        '/api/v1/auth/login': {
            'methods': ['POST'],
            'description': 'Login user and get JWT token',
            'requires_auth': False,
            'parameters': [
                {'name': 'username', 'type': 'string', 'required': True},
                {'name': 'password', 'type': 'string', 'required': True}
            ]
        },
        '/api/v1/auth/logout': {
            'methods': ['POST'],
            'description': 'Logout user (client-side token removal)',
            'requires_auth': True,
            'parameters': []
        },
        '/api/v1/auth/profile': {
            'methods': ['GET', 'PUT'],
            'description': 'Get or update current user profile',
            'requires_auth': True,
            'parameters': [
                {'name': 'name', 'type': 'string', 'required': False},
                {'name': 'email', 'type': 'string', 'required': False},
                {'name': 'role', 'type': 'string', 'required': False},
                {'name': 'department', 'type': 'string', 'required': False},
                {'name': 'phone', 'type': 'string', 'required': False}
            ]
        },
        
        # Anomaly Management endpoints
        '/api/v1/anomalies': {
            'methods': ['GET', 'POST'],
            'description': 'List all anomalies or create new anomaly',
            'requires_auth': True,
            'parameters': [
                {'name': 'num_equipement', 'type': 'string', 'required': True},
                {'name': 'systeme', 'type': 'string', 'required': True},
                {'name': 'description', 'type': 'string', 'required': True},
                {'name': 'date_detection', 'type': 'string', 'required': True},
                {'name': 'description_equipement', 'type': 'string', 'required': True},
                {'name': 'section_proprietaire', 'type': 'string', 'required': True},
                {'name': 'page', 'type': 'integer', 'required': False, 'location': 'query'},
                {'name': 'per_page', 'type': 'integer', 'required': False, 'location': 'query'}
            ]
        },
        '/api/v1/anomalies/<id>': {
            'methods': ['GET', 'PUT', 'DELETE'],
            'description': 'Get, update or delete specific anomaly',
            'requires_auth': True,
            'parameters': [
                {'name': 'id', 'type': 'integer', 'required': True, 'location': 'path'},
                {'name': 'description', 'type': 'string', 'required': False},
                {'name': 'status', 'type': 'string', 'required': False},
                {'name': 'priority', 'type': 'string', 'required': False}
            ]
        },
        '/api/v1/anomalies/<id>/approve': {
            'methods': ['POST'],
            'description': 'Approve anomaly predictions',
            'requires_auth': True,
            'parameters': [
                {'name': 'id', 'type': 'integer', 'required': True, 'location': 'path'}
            ]
        },
        '/api/v1/anomalies/<id>/predictions': {
            'methods': ['PUT'],
            'description': 'Edit anomaly predictions',
            'requires_auth': True,
            'parameters': [
                {'name': 'id', 'type': 'integer', 'required': True, 'location': 'path'},
                {'name': 'fiabilite_score', 'type': 'number', 'required': False},
                {'name': 'disponibilite_score', 'type': 'number', 'required': False},
                {'name': 'process_safety_score', 'type': 'number', 'required': False},
                {'name': 'criticality_level', 'type': 'number', 'required': False}
            ]
        },
        '/api/v1/anomalies/<id>/status': {
            'methods': ['PUT'],
            'description': 'Update anomaly status',
            'requires_auth': True,
            'parameters': [
                {'name': 'id', 'type': 'integer', 'required': True, 'location': 'path'},
                {'name': 'status', 'type': 'string', 'required': True}
            ]
        },
        '/api/v1/anomalies/batch': {
            'methods': ['POST'],
            'description': 'Create multiple anomalies at once',
            'requires_auth': True,
            'parameters': [
                {'name': 'anomalies', 'type': 'array', 'required': True}
            ]
        },
        '/api/v1/anomalies/upload': {
            'methods': ['POST'],
            'description': 'Upload file with anomalies (CSV or Excel)',
            'requires_auth': True,
            'parameters': [
                {'name': 'file', 'type': 'file', 'required': True}
            ]
        },
        '/api/v1/anomalies/bulk/status': {
            'methods': ['PUT'],
            'description': 'Update multiple anomalies status at once',
            'requires_auth': True,
            'parameters': [
                {'name': 'anomaly_ids', 'type': 'array', 'required': True},
                {'name': 'status', 'type': 'string', 'required': True}
            ]
        },
        
        # Maintenance windows endpoints
        '/api/v1/maintenance-windows': {
            'methods': ['GET', 'POST'],
            'description': 'List all maintenance windows or create new window',
            'requires_auth': True,
            'parameters': [
                {'name': 'type', 'type': 'string', 'required': True},
                {'name': 'duration_days', 'type': 'integer', 'required': True},
                {'name': 'start_date', 'type': 'string', 'required': True},
                {'name': 'description', 'type': 'string', 'required': False}
            ]
        },
        '/api/v1/maintenance-windows/<id>': {
            'methods': ['GET', 'PUT', 'DELETE'],
            'description': 'Get, update or delete maintenance window',
            'requires_auth': True,
            'parameters': [
                {'name': 'id', 'type': 'integer', 'required': True, 'location': 'path'},
                {'name': 'type', 'type': 'string', 'required': False},
                {'name': 'duration_days', 'type': 'integer', 'required': False},
                {'name': 'start_date', 'type': 'string', 'required': False},
                {'name': 'description', 'type': 'string', 'required': False},
                {'name': 'status', 'type': 'string', 'required': False}
            ]
        },
        '/api/v1/maintenance-windows/<id>/schedule-anomaly': {
            'methods': ['POST'],
            'description': 'Schedule anomaly to maintenance window',
            'requires_auth': True,
            'parameters': [
                {'name': 'id', 'type': 'integer', 'required': True, 'location': 'path'},
                {'name': 'anomaly_id', 'type': 'integer', 'required': True}
            ]
        },
        
        # Action plan endpoints
        '/api/v1/action-plans/<anomaly_id>': {
            'methods': ['GET', 'POST', 'PUT'],
            'description': 'Get, create or update action plan for anomaly',
            'requires_auth': True,
            'parameters': [
                {'name': 'anomaly_id', 'type': 'integer', 'required': True, 'location': 'path'},
                {'name': 'needs_outage', 'type': 'boolean', 'required': False},
                {'name': 'outage_type', 'type': 'string', 'required': False},
                {'name': 'outage_duration', 'type': 'integer', 'required': False},
                {'name': 'planned_date', 'type': 'string', 'required': False},
                {'name': 'total_duration_hours', 'type': 'number', 'required': False},
                {'name': 'estimated_cost', 'type': 'number', 'required': False},
                {'name': 'priority', 'type': 'string', 'required': False},
                {'name': 'comments', 'type': 'string', 'required': False}
            ]
        },
        '/api/v1/action-plans/<action_plan_id>/items': {
            'methods': ['POST'],
            'description': 'Add action item to action plan',
            'requires_auth': True,
            'parameters': [
                {'name': 'action_plan_id', 'type': 'integer', 'required': True, 'location': 'path'},
                {'name': 'action', 'type': 'string', 'required': True},
                {'name': 'responsable', 'type': 'string', 'required': False},
                {'name': 'pdrs_disponible', 'type': 'boolean', 'required': False},
                {'name': 'duree_heures', 'type': 'number', 'required': False}
            ]
        },
        '/api/v1/action-plans/<action_plan_id>/items/<item_id>': {
            'methods': ['PUT', 'DELETE'],
            'description': 'Update or delete action item',
            'requires_auth': True,
            'parameters': [
                {'name': 'action_plan_id', 'type': 'integer', 'required': True, 'location': 'path'},
                {'name': 'item_id', 'type': 'integer', 'required': True, 'location': 'path'},
                {'name': 'action', 'type': 'string', 'required': False},
                {'name': 'responsable', 'type': 'string', 'required': False},
                {'name': 'pdrs_disponible', 'type': 'boolean', 'required': False},
                {'name': 'statut', 'type': 'string', 'required': False},
                {'name': 'duree_heures', 'type': 'number', 'required': False}
            ]
        },
        
        # Dashboard endpoints
        '/api/v1/dashboard/metrics': {
            'methods': ['GET'],
            'description': 'Get dashboard overview metrics',
            'requires_auth': True,
            'parameters': []
        },
        '/api/v1/dashboard/charts/anomalies-by-month': {
            'methods': ['GET'],
            'description': 'Get anomalies count by month',
            'requires_auth': True,
            'parameters': [
                {'name': 'year', 'type': 'integer', 'required': False, 'location': 'query'}
            ]
        },
        '/api/v1/dashboard/charts/anomalies-by-service': {
            'methods': ['GET'],
            'description': 'Get anomalies count by service department',
            'requires_auth': True,
            'parameters': []
        },
        '/api/v1/dashboard/charts/anomalies-by-criticality': {
            'methods': ['GET'],
            'description': 'Get anomalies count by criticality level',
            'requires_auth': True,
            'parameters': []
        },
        '/api/v1/dashboard/charts/maintenance-windows': {
            'methods': ['GET'],
            'description': 'Get maintenance windows timeline',
            'requires_auth': True,
            'parameters': []
        },
        
        # Prediction endpoints
        '/api/v1/predict': {
            'methods': ['GET', 'POST'],
            'description': 'Get prediction for equipment reliability',
            'requires_auth': True,
            'parameters': [
                {'name': 'num_equipement', 'type': 'string', 'required': True},
                {'name': 'systeme', 'type': 'string', 'required': True},
                {'name': 'description', 'type': 'string', 'required': True}
            ]
        },
        '/api/v1/predict-batch': {
            'methods': ['POST'],
            'description': 'Get predictions for multiple equipment items',
            'requires_auth': True,
            'parameters': [
                {'name': 'items', 'type': 'array', 'required': True}
            ]
        },
        '/api/v1/predict-file': {
            'methods': ['POST'],
            'description': 'Upload file and get predictions (CSV or Excel)',
            'requires_auth': True,
            'parameters': [
                {'name': 'file', 'type': 'file', 'required': True}
            ]
        },
        
        # Import endpoints
        '/api/v1/import/anomalies': {
            'methods': ['POST'],
            'description': 'Import anomalies from file',
            'requires_auth': True,
            'parameters': [
                {'name': 'file', 'type': 'file', 'required': True}
            ]
        }
    }
    
    return endpoints_info

@browsable_api.route('/endpoints')
def endpoints():
    """List all available endpoints"""
    # Get endpoints from the current app
    endpoints_info = get_endpoints_info()
    
    return render_template('api_browser/endpoints.html', endpoints=endpoints_info)

@browsable_api.route('/endpoints/<path:endpoint_path>')
def test_endpoint(endpoint_path):
    """Page to test a specific endpoint"""
    endpoint = f'/api/v1/{endpoint_path}'
    
    # Get all endpoints info and find the specific one
    endpoints_info = get_endpoints_info()
    endpoint_info = endpoints_info.get(endpoint)
    
    if not endpoint_info:
        # Default info
        endpoint_info = {
            'path': endpoint,
            'methods': ['GET', 'POST', 'PUT', 'DELETE'],
            'parameters': []
        }
    
    return render_template('api_browser/test_endpoint.html', endpoint=endpoint, endpoint_info=endpoint_info)

@browsable_api.route('/login', methods=['GET', 'POST'])
def login():
    """Login to the API browser"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash("Username and password are required", "error")
            return render_template('api_browser/login.html')
        
        try:
            # Make actual login request to our API
            response = requests.post(
                f"{request.url_root.rstrip('/')}/api/v1/auth/login",
                json={'username': username, 'password': password}
            )
            
            if response.status_code == 200:
                # Login successful
                data = response.json()
                session['user'] = data['user']
                session['auth_token'] = data['access_token']
                flash("Login successful", "success")
                return redirect(url_for('browsable_api.index'))
            else:
                error_msg = response.json().get('error', 'Invalid credentials')
                flash(error_msg, "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        
        return render_template('api_browser/login.html')
    
    return render_template('api_browser/login.html')

@browsable_api.route('/logout')
def logout():
    """Logout from the API browser"""
    session.pop('user', None)
    session.pop('auth_token', None)
    flash("You have been logged out", "success")
    return redirect(url_for('browsable_api.index'))

@browsable_api.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash("All fields are required", "error")
            return render_template('api_browser/register.html')
        
        try:
            # Make actual registration request to our API
            response = requests.post(
                f"{request.url_root.rstrip('/')}/api/v1/auth/register",
                json={'username': username, 'email': email, 'password': password}
            )
            
            if response.status_code == 201:
                # Registration successful
                data = response.json()
                session['user'] = data['user']
                session['auth_token'] = data['access_token']
                flash("Registration successful", "success")
                return redirect(url_for('browsable_api.index'))
            else:
                error_msg = response.json().get('error', 'Registration failed')
                flash(error_msg, "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        
        return render_template('api_browser/register.html')
    
    return render_template('api_browser/register.html')

@browsable_api.route('/api-request', methods=['POST'])
@browsable_api.route('/api-call', methods=['POST'])  # Adding alias for backward compatibility
def make_api_request():
    """Make an API request and return the result"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    method = data.get('method', 'GET')
    endpoint = data.get('url') or data.get('endpoint')
    payload = data.get('data') or data.get('payload', {})
    
    if not endpoint:
        return jsonify({"error": "No endpoint provided"}), 400
    
    headers = {}
    if session.get('auth_token'):
        headers['Authorization'] = f"Bearer {session['auth_token']}"
    
    try:
        url = f"{request.url_root.rstrip('/')}{endpoint}"
        
        if method.upper() == 'GET':
            response = requests.get(url, params=payload, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=payload, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=payload, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, json=payload, headers=headers)
        else:
            return jsonify({"error": "Unsupported method"}), 400
        
        return jsonify({
            "status": response.status_code,
            "data": response.json() if response.text else {}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
