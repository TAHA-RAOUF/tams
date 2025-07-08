#!/usr/bin/env python3
"""
TAMS - Technical Asset Management System
Main application entry point
"""
import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Print startup information
    print(f"\n🚀 Starting TAMS API server on port {port}")
    print("=" * 60)
    print("📋 API Endpoints:")
    
    print("\n  Authentication:")
    print("    - POST /api/v1/auth/register - Create new user account")
    print("    - POST /api/v1/auth/login - Login and get JWT token")
    print("    - POST /api/v1/auth/logout - Logout user (client-side)")
    print("    - GET/PUT /api/v1/auth/profile - Get/update user profile (JWT required)")
    
    print("\n  Anomaly Management (JWT required):")
    print("    - GET /api/v1/anomalies - Get all anomalies with pagination")
    print("    - POST /api/v1/anomalies - Create single anomaly with prediction")
    print("    - GET /api/v1/anomalies/<id> - Get specific anomaly")
    print("    - PUT /api/v1/anomalies/<id> - Update anomaly")
    print("    - DELETE /api/v1/anomalies/<id> - Delete anomaly")
    print("    - POST /api/v1/anomalies/<id>/approve - Approve anomaly predictions")
    print("    - PUT /api/v1/anomalies/<id>/predictions - Edit anomaly predictions")
    print("    - PUT /api/v1/anomalies/<id>/status - Update anomaly status with flow validation")
    print("    - PUT /api/v1/anomalies/bulk/status - Update multiple anomalies' statuses")
    print("    - POST /api/v1/anomalies/batch - Create multiple anomalies")
    print("    - POST /api/v1/anomalies/upload - Upload CSV/Excel file")
    
    print("\n  Maintenance Windows (JWT required):")
    print("    - GET /api/v1/maintenance-windows - Get all maintenance windows with filtering")
    print("    - POST /api/v1/maintenance-windows - Create maintenance window")
    print("    - GET /api/v1/maintenance-windows/<id> - Get specific window")
    print("    - PUT /api/v1/maintenance-windows/<id> - Update window")
    print("    - DELETE /api/v1/maintenance-windows/<id> - Delete window")
    print("    - POST /api/v1/maintenance-windows/<id>/schedule-anomaly - Schedule anomaly to window")
    
    print("\n  Action Plans (JWT required):")
    print("    - POST /api/v1/action-plans/<anomaly_id> - Create action plan")
    print("    - GET /api/v1/action-plans/<anomaly_id> - Get action plan")
    print("    - PUT /api/v1/action-plans/<anomaly_id> - Update action plan")
    print("    - POST /api/v1/action-plans/<id>/items - Add action item")
    print("    - PUT /api/v1/action-plans/<id>/items/<item_id> - Update action item")
    print("    - DELETE /api/v1/action-plans/<id>/items/<item_id> - Delete action item")
    
    print("\n  Dashboard & Reporting (JWT required):")
    print("    - GET /api/v1/dashboard/metrics - Get overview metrics")
    print("    - GET /api/v1/dashboard/charts/anomalies-by-month - Get anomalies by month")
    print("    - GET /api/v1/dashboard/charts/anomalies-by-service - Get anomalies by service")
    print("    - GET /api/v1/dashboard/charts/anomalies-by-criticality - Get anomalies by criticality")
    print("    - GET /api/v1/dashboard/charts/maintenance-windows - Get maintenance window timeline")
    
    print("\n  Data Import (JWT required):")
    print("    - POST /api/v1/import/anomalies - Import anomalies from file")
    
    print("\n  Direct Predictions (JWT required):")
    print("    - GET/POST /api/v1/predict - Single equipment reliability prediction")
    print("    - POST /api/v1/predict-batch - Batch equipment reliability prediction")
    print("    - POST /api/v1/predict-file - File-based prediction")
    
    print("\nFeatures for ML prediction: Num_equipement, Systeme, Description")
    print("Predicted outputs: Fiabilité Intégrité, Disponibilité, Process Safety")
    print("Criticality is calculated as sum of the three scores")
    
    print("\n🎯 Use the browsable API at http://localhost:5000/api-browser/ for easy testing!")
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=debug)
