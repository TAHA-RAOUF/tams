# TAMS - Technical Asset Management System

## Project Overview

TAMS is a Flask-based API for managing technical assets, predicting equipment reliability, and organizing maintenance actions.

## Project Structure

The project follows a modular structure:

```
/tams/
├── app/                      # Main application package
│   ├── __init__.py           # App factory function
│   ├── api/                  # API definition package
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/     # API endpoint modules
│   │           ├── __init__.py
│   │           ├── action_plans.py
│   │           ├── anomalies.py
│   │           ├── auth.py
│   │           ├── dashboard.py
│   │           ├── import_data.py
│   │           ├── maintenance.py
│   │           ├── predictions.py
│   │           └── status.py
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── browsable_api.py
│   │   ├── error_handlers.py
│   │   └── predictor.py
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── action_plan.py
│   │   ├── anomaly.py
│   │   ├── database.py
│   │   ├── maintenance.py
│   │   └── user.py
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   └── enhanced_auth.py
│   ├── templates/            # HTML templates
│   ├── static/               # Static assets
│   └── docs/                 # API documentation
├── scripts/                  # Utility scripts
│   ├── init_db.py
│   ├── seed_database.py
│   ├── inspect_data.py
│   ├── inspect_model.py
│   └── cleanup.py
├── ml_models/                # ML model files
│   ├── model.py
│   └── multi_output_model.pkl
├── swagger_specs/            # API documentation
│   ├── anomalies.yml
│   ├── login.yml
│   ├── predict_batch.yml
│   ├── predict_file.yml
│   ├── predict.yml
│   ├── profile.yml
│   └── register.yml
├── run.py                    # Application entry point
└── requirements.txt          # Dependencies
```

## Setup and Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```
   python scripts/init_db.py
   ```
5. Seed the database (optional):
   ```
   python scripts/seed_database.py
   ```

## Running the Application

Start the Flask development server:
```
python run.py
```

Or with Flask CLI:
```
export FLASK_APP=run.py
export FLASK_DEBUG=1  # For development
flask run
```

The API will be available at `http://localhost:5000/`.

## API Documentation

Browse the API documentation and test the endpoints at:
```
http://localhost:5000/api-browser/
```

## ML Model

The system uses a pre-trained ML model to predict:
- Fiabilité Intégrité
- Disponibilité
- Process Safety

Features used for prediction:
- Num_equipement
- Systeme
- Description
