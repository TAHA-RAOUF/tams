# TAMS - Technical Asset Management System

This API provides a comprehensive backend for managing technical assets, anomaly detection, maintenance planning, and prediction using AI.

## Project Structure

The project has been reorganized to follow modern Flask application structure conventions:

```
tams/
├── app/                  # Main application package
│   ├── __init__.py       # Application factory
│   ├── api/              # API resources
│   │   ├── __init__.py
│   │   └── v1/           # API version 1
│   │       ├── __init__.py
│   │       └── endpoints/  # API endpoints
│   ├── core/             # Core application logic
│   ├── models/           # Database models
│   ├── utils/            # Utility functions
│   ├── templates/        # Template files
│   ├── static/           # Static files
│   └── docs/             # Documentation files
├── scripts/              # Utility scripts
├── run.py                # Application entry point
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## System Components

### Authentication & User Management
- Complete user registration and authentication system using JWT
- Profile management with role-based permissions
- Secure password hashing with bcrypt

### Anomaly Management
- Create, retrieve, update, and delete anomalies
- AI-based prediction of criticality scores
- Status workflow management (open, in_progress, resolved, closed)
- Batch operations for efficient handling

### Maintenance Planning
- Maintenance window scheduling
- Action plans for anomalies
- Task breakdown with action items
- Resource allocation and tracking

### Dashboard & Reporting
- Key metrics and KPIs
- Charts and visualizations
- Timeline views for maintenance windows
- Criticality distribution analysis

### Data Import/Export
- Import anomalies from CSV/Excel files
- Column mapping for flexible import
- Validation and error reporting
- Batch processing with AI prediction

### AI Integration
- Equipment reliability prediction
- Criticality scoring based on multiple factors
- Manual override capabilities
- Batch prediction for multiple items
- **Batch Processing**: Handle multiple anomalies at once
- **File Upload**: Process CSV/Excel files
- **API Documentation**: Swagger/OpenAPI documentation

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user (client-side)
- `GET/PUT /api/v1/auth/profile` - Get/update user profile

### Anomaly Management
- `GET /api/v1/anomalies` - Get all anomalies with pagination
- `POST /api/v1/anomalies` - Create single anomaly with prediction
- `GET /api/v1/anomalies/<id>` - Get specific anomaly
- `PUT /api/v1/anomalies/<id>` - Update anomaly
- `DELETE /api/v1/anomalies/<id>` - Delete anomaly
- `POST /api/v1/anomalies/<id>/approve` - Approve anomaly predictions
- `PUT /api/v1/anomalies/<id>/predictions` - Edit anomaly predictions
- `PUT /api/v1/anomalies/<id>/status` - Update anomaly status with flow validation
- `PUT /api/v1/anomalies/bulk/status` - Update multiple anomalies' statuses
- `POST /api/v1/anomalies/batch` - Create multiple anomalies
- `POST /api/v1/anomalies/upload` - Upload CSV/Excel file

### Maintenance Windows
- `GET /api/v1/maintenance-windows` - Get all maintenance windows with filtering
- `POST /api/v1/maintenance-windows` - Create maintenance window
- `GET /api/v1/maintenance-windows/<id>` - Get specific window
- `PUT /api/v1/maintenance-windows/<id>` - Update window
- `DELETE /api/v1/maintenance-windows/<id>` - Delete window
- `POST /api/v1/maintenance-windows/<id>/schedule-anomaly` - Schedule anomaly to window

### Action Plans
- `POST /api/v1/action-plans/<anomaly_id>` - Create action plan
- `GET /api/v1/action-plans/<anomaly_id>` - Get action plan
- `PUT /api/v1/action-plans/<anomaly_id>` - Update action plan
- `POST /api/v1/action-plans/<id>/items` - Add action item
- `PUT /api/v1/action-plans/<id>/items/<item_id>` - Update action item
- `DELETE /api/v1/action-plans/<id>/items/<item_id>` - Delete action item

### Dashboard & Reporting
- `GET /api/v1/dashboard/metrics` - Get overview metrics
- `GET /api/v1/dashboard/charts/anomalies-by-month` - Get anomalies by month
- `GET /api/v1/dashboard/charts/anomalies-by-service` - Get anomalies by service
- `GET /api/v1/dashboard/charts/anomalies-by-criticality` - Get anomalies by criticality
- `GET /api/v1/dashboard/charts/maintenance-windows` - Get maintenance window timeline

### Data Import
- `POST /api/v1/import/anomalies` - Import anomalies from file

### Direct Predictions
- `GET/POST /api/v1/predict` - Single equipment reliability prediction
- `POST /api/v1/predict-batch` - Batch equipment reliability prediction
- `POST /api/v1/predict-file` - File-based prediction

## Tech Stack

- **Backend**: Flask with Flask-RESTful, SQLAlchemy
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT with Flask-JWT-Extended
- **AI/ML**: scikit-learn for prediction models
- **Data Processing**: pandas for data manipulation
- **API Documentation**: Browsable API interface

## Setup & Running

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   python init_db.py
   ```

4. Seed the database with sample data (optional):
   ```
   python seed_database.py
   ```

5. Start the API server:
   ```
   python main.py
   ```

6. Access the browsable API at http://localhost:5000/api-browser/

## AI Model

The system uses a machine learning model that predicts three key scores:
- Fiabilité Intégrité (Equipment Reliability & Integrity)
- Disponibilité (Availability)
- Process Safety

The overall criticality is calculated as the sum of these three scores.

## Data Format

### Anomaly Data
The API expects anomaly data in the following format:

```json
{
  "num_equipement": "7d34d01e-6874-40c0-bbdc-77b8bc8ebba8",
  "systeme": "8ab799f5-144f-420c-b426-3d7e36b13f59",
  "description": "clapet du circuit de ramoange non étanche",
  "date_detection": "2019-01-01 10:09:10",
  "description_equipement": "Soupape",
  "section_proprietaire": "34MC"
}
```

### Maintenance Windows
For creating maintenance windows:

```json
{
  "type": "planned",
  "duration_days": 7,
  "start_date": "2025-08-01T08:00:00Z",
  "description": "Annual equipment maintenance",
  "status": "scheduled"
}
```

### Action Plans
For creating action plans:

```json
{
  "needs_outage": true,
  "outage_type": "planned",
  "planned_date": "2025-08-05T10:00:00Z",
  "total_duration_hours": 48,
  "estimated_cost": 25000,
  "priority": "high",
  "comments": "Critical maintenance required",
  "action_items": [
    {
      "action": "Replace valve assembly",
      "responsable": "Maintenance Team A",
      "pdrs_disponible": true,
      "ressources_internes": "2 technicians",
      "duree_heures": 8
    },
    {
      "action": "System testing",
      "responsable": "QA Team",
      "duree_heures": 4
    }
  ]
}
```

## Project Structure
```
tams/
├── main.py                   # Flask application entry point
├── models.py                 # Database models
├── auth.py                   # Authentication endpoints
├── anomaly_api.py            # Anomaly management endpoints
├── maintenance_api.py        # Maintenance window & action plan endpoints
├── dashboard_api.py          # Reporting & metrics endpoints
├── import_api.py             # Data import endpoints
├── anomaly_status_api.py     # Status flow management endpoints
├── api.py                    # Prediction endpoints
├── predictor.py              # ML prediction logic
├── browsable_api.py          # Interactive API browser
├── requirements.txt          # Python dependencies
├── init_db.py                # Database initialization
├── seed_database.py          # Sample data generator
├── inspect_model.py          # Model inspection utility
├── inspect_data.py           # Data inspection utility
├── ml_models/                # ML model files
│   ├── model.py              # Model training script
│   ├── multi_output_model.pkl # Trained ML model
│   └── Taqathon_data_01072025.xlsx # Training data
└── templates/                # HTML templates for browsable API
    └── api_browser/          # API browser templates
```

## Development

To run the API in debug mode:
```
FLASK_DEBUG=true python main.py
```

To inspect the ML model:
```
python inspect_model.py
```

To inspect the training data:
```
python inspect_data.py
```

## Features Overview

### Status Flow Management
- Anomalies follow a defined status flow: open → in_progress → resolved → closed
- API enforces valid state transitions
- Status changes are tracked with timestamps and user information
- Bulk status updates for efficient management

### Maintenance Window Management
- Schedule planned and emergency maintenance periods
- Assign anomalies to specific maintenance windows
- Track maintenance window status (scheduled, in_progress, completed)
- Filter and search maintenance windows by date, type, and status

### Action Plan Management
- Create detailed action plans for anomalies
- Break down plans into specific action items
- Track resources, responsible parties, and time estimates
- Monitor action item status and progress

### Reporting & Analytics
- Get key metrics about anomalies and maintenance
- View anomaly distribution by month, service, and criticality
- Track average resolution times and anomaly trends
- Generate data for timeline and calendar views

### Data Import & Export
- Import anomalies from CSV/Excel files
- Flexible column mapping for varied file formats
- Validation and error reporting during import
- Bulk operations with AI predictions automatically applied
   - View all anomalies in the system
   - Click "Approve" button → sets `is_approved = true` with their user ID
   - Edit predictions manually → automatically sets `is_approved = true` with their user ID
   - Update or delete any anomaly

### Database Schema Updates

```sql
-- Updated anomalies table:
created_by_user_id INTEGER REFERENCES users(id),    -- Who created
updated_by_user_id INTEGER REFERENCES users(id),    -- Who last updated  
approved_by_user_id INTEGER REFERENCES users(id),   -- Who approved
is_approved BOOLEAN DEFAULT FALSE NOT NULL,
approved_at TIMESTAMP NULL
```

### User Tracking

The system now tracks:
- **created_by_user_id**: Who originally created the anomaly
- **updated_by_user_id**: Who last updated the anomaly data
- **approved_by_user_id**: Who approved the predictions
- **Timestamps**: When each action occurred

This provides full audit trail while allowing collaborative access to all anomalies.

## License

This project is part of the TAQATHON competition.
