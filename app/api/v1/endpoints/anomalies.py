# anomalies.py
from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from app.models import db, Anomaly, User
from app.core.predictor import EquipmentReliabilityPredictor
from datetime import datetime
import pandas as pd
import io

class AnomalyListAPI(Resource):
    @jwt_required()
    def get(self):
        """Get all anomalies (accessible to all users)"""
        try:
            # Get all anomalies with pagination - accessible to all users
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            anomalies = Anomaly.query\
                .order_by(Anomaly.created_at.desc())\
                .paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                "anomalies": [anomaly.to_dict() for anomaly in anomalies.items],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": anomalies.total,
                    "pages": anomalies.pages
                }
            }, 200
            
        except Exception as e:
            return {"error": str(e)}, 500

class AnomalyAPI(Resource):
    @jwt_required()
    def get(self, anomaly_id=None):
        """Get a specific anomaly or all anomalies (accessible to all users)"""
        try:
            if anomaly_id:
                # Get specific anomaly - accessible to all users
                anomaly = Anomaly.query.get(anomaly_id)
                if not anomaly:
                    return {"error": "Anomaly not found"}, 404
                return {"anomaly": anomaly.to_dict()}, 200
            else:
                # Get all anomalies with pagination - accessible to all users
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 20, type=int)
                
                anomalies = Anomaly.query\
                    .order_by(Anomaly.created_at.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)
                
                return {
                    "anomalies": [anomaly.to_dict() for anomaly in anomalies.items],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": anomalies.total,
                        "pages": anomalies.pages
                    }
                }, 200
                
        except Exception as e:
            return {"error": str(e)}, 500
    
    @jwt_required()
    def post(self):
        """Create and predict a single anomaly"""
        try:
            current_user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            # Validate required fields
            required_fields = ["num_equipement", "systeme", "description", "date_detection", "description_equipement", "section_proprietaire"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {"error": f"Missing required fields: {missing_fields}"}, 400
            
            # Parse date
            try:
                date_detection = datetime.fromisoformat(data['date_detection'].replace('Z', '+00:00'))
            except:
                try:
                    date_detection = datetime.strptime(data['date_detection'], '%Y-%m-%d %H:%M:%S')
                except:
                    return {"error": "Invalid date format. Use ISO format or 'YYYY-MM-DD HH:MM:SS'"}, 400
            
            # Create anomaly record
            anomaly = Anomaly(
                num_equipement=data['num_equipement'],
                systeme=data['systeme'],
                description=data['description'],
                date_detection=date_detection,
                description_equipement=data['description_equipement'],
                section_proprietaire=data['section_proprietaire'],
                created_by_user_id=current_user_id
            )
            
            # Make prediction using the correct features: Num_equipement, Systeme, Description
            try:
                predictor = EquipmentReliabilityPredictor()
                prediction_input = {
                    "Num_equipement": data['num_equipement'],
                    "Systeme": data['systeme'],
                    "Description": data['description']
                }
                predictions = predictor.predict_single(prediction_input)
                anomaly.update_predictions(predictions)
            except Exception as e:
                print(f"Prediction error: {str(e)}")
                # Save without predictions if prediction fails
                pass
            
            db.session.add(anomaly)
            db.session.commit()
            
            return {
                "message": "Anomaly created and predicted successfully",
                "anomaly": anomaly.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def put(self, anomaly_id):
        """Update an anomaly (accessible to all users). If closing, require REX file upload."""
        try:
            current_user_id = int(get_jwt_identity())
            anomaly = Anomaly.query.get(anomaly_id)
            if not anomaly:
                return {"error": "Anomaly not found"}, 404

            # Check if this is a multipart/form-data request (for file upload)
            if request.content_type and request.content_type.startswith('multipart/form-data'):
                data = request.form.to_dict()
                rex_file = request.files.get('rex_file')
            else:
                data = request.get_json() or {}
                rex_file = None

            # Update fields
            updatable_fields = ['description', 'description_equipement', 'section_proprietaire', 'status']
            for field in updatable_fields:
                if field in data:
                    setattr(anomaly, field, data[field])

            # If status is being set to 'closed', require REX file
            if data.get('status') == 'closed':
                if not rex_file:
                    return {"error": "REX file is required to close an anomaly."}, 400
                # Upload to S3
                from app.core.s3_utils import upload_file_to_s3
                import os
                bucket = os.environ.get('REX_S3_BUCKET')
                if not bucket:
                    return {"error": "S3 bucket not configured (REX_S3_BUCKET)."}, 500
                key = f"rex_files/anomaly_{anomaly.id}_{rex_file.filename}"
                success, s3_url = upload_file_to_s3(rex_file, bucket, key, rex_file.content_type)
                if not success:
                    return {"error": f"Failed to upload REX file: {s3_url}"}, 500
                anomaly.rex_file = s3_url

            # Track who updated
            anomaly.updated_by_user_id = current_user_id

            # Re-predict if relevant fields changed
            if any(field in data for field in ['description', 'description_equipement', 'section_proprietaire']):
                try:
                    predictor = EquipmentReliabilityPredictor()
                    prediction_input = {
                        "Num_equipement": anomaly.num_equipement,
                        "Systeme": anomaly.systeme,
                        "Description": anomaly.description
                    }
                    predictions = predictor.predict_single(prediction_input)
                    anomaly.update_predictions(predictions)
                except Exception as e:
                    print(f"Prediction error: {str(e)}")

            db.session.commit()

            return {
                "message": "Anomaly updated successfully",
                "anomaly": anomaly.to_dict()
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def delete(self, anomaly_id):
        """Delete an anomaly (accessible to all users)"""
        try:
            anomaly = Anomaly.query.get(anomaly_id)
            
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            db.session.delete(anomaly)
            db.session.commit()
            
            return {"message": "Anomaly deleted successfully"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class BatchAnomalyAPI(Resource):
    @jwt_required()
    def post(self):
        """Create and predict multiple anomalies in batch"""
        try:
            current_user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data or 'anomalies' not in data:
                return {"error": "No anomalies data provided"}, 400
            
            anomalies_data = data['anomalies']
            if not isinstance(anomalies_data, list):
                return {"error": "Anomalies must be a list"}, 400
            
            created_anomalies = []
            predictor = EquipmentReliabilityPredictor()
            
            for anomaly_data in anomalies_data:
                # Validate required fields
                required_fields = ["num_equipement", "systeme", "description", "date_detection", "description_equipement", "section_proprietaire"]
                missing_fields = [field for field in required_fields if field not in anomaly_data]
                if missing_fields:
                    continue  # Skip invalid records
                
                # Parse date
                try:
                    date_detection = datetime.fromisoformat(anomaly_data['date_detection'].replace('Z', '+00:00'))
                except:
                    try:
                        date_detection = datetime.strptime(anomaly_data['date_detection'], '%Y-%m-%d %H:%M:%S')
                    except:
                        continue  # Skip invalid dates
                
                # Create anomaly
                anomaly = Anomaly(
                    num_equipement=anomaly_data['num_equipement'],
                    systeme=anomaly_data['systeme'],
                    description=anomaly_data['description'],
                    date_detection=date_detection,
                    description_equipement=anomaly_data['description_equipement'],
                    section_proprietaire=anomaly_data['section_proprietaire'],
                    created_by_user_id=current_user_id
                )
                
                # Make prediction
                try:
                    prediction_input = {
                        "Num_equipement": anomaly_data['num_equipement'],
                        "Systeme": anomaly_data['systeme'],
                        "Description": anomaly_data['description']
                    }
                    predictions = predictor.predict_single(prediction_input)
                    anomaly.update_predictions(predictions)
                except Exception as e:
                    print(f"Prediction error for anomaly: {str(e)}")
                
                db.session.add(anomaly)
                created_anomalies.append(anomaly)
            
            db.session.commit()
            
            return {
                "message": f"Created {len(created_anomalies)} anomalies successfully",
                "anomalies": [anomaly.to_dict() for anomaly in created_anomalies]
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class FileAnomalyAPI(Resource):
    @jwt_required()
    def post(self):
        """Upload and process anomalies from CSV/Excel file"""
        try:
            current_user_id = int(get_jwt_identity())
            
            # Check if file is in the request
            if 'file' not in request.files:
                return {"error": "No file provided"}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {"error": "No file selected"}, 400
            
            # Read file based on extension
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
                elif file.filename.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file)
                else:
                    return {"error": "File must be CSV or Excel format"}, 400
            except Exception as e:
                return {"error": f"Error reading file: {str(e)}"}, 400
            
            # Validate columns
            required_columns = ["Num_equipement", "Systeme", "Description", "Date de détéction de l'anomalie", "Description de l'équipement", "Section propriétaire"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {"error": f"Missing required columns: {missing_columns}"}, 400
            
            created_anomalies = []
            predictor = EquipmentReliabilityPredictor()
            
            for _, row in df.iterrows():
                try:
                    # Parse date
                    date_detection = pd.to_datetime(row["Date de détéction de l'anomalie"])
                    
                    # Create anomaly
                    anomaly = Anomaly(
                        num_equipement=str(row["Num_equipement"]),
                        systeme=str(row["Systeme"]),
                        description=str(row["Description"]),
                        date_detection=date_detection,
                        description_equipement=str(row["Description de l'équipement"]),
                        section_proprietaire=str(row["Section propriétaire"]),
                        created_by_user_id=current_user_id
                    )
                    
                    # Make prediction
                    try:
                        prediction_input = {
                            "Num_equipement": str(row["Num_equipement"]),
                            "Systeme": str(row["Systeme"]),
                            "Description": str(row["Description"])
                        }
                        predictions = predictor.predict_single(prediction_input)
                        anomaly.update_predictions(predictions)
                    except Exception as e:
                        print(f"Prediction error for row: {str(e)}")
                    
                    db.session.add(anomaly)
                    created_anomalies.append(anomaly)
                    
                except Exception as e:
                    print(f"Error processing row: {str(e)}")
                    continue
            
            db.session.commit()
            
            return {
                "message": f"Processed {len(created_anomalies)} anomalies from file",
                "total_rows": len(df),
                "successful_rows": len(created_anomalies),
                "anomalies": [anomaly.to_dict() for anomaly in created_anomalies[:10]]  # Show first 10
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class AnomalyApprovalAPI(Resource):
    @jwt_required()
    def post(self, anomaly_id):
        """Approve an anomaly's predictions (accessible to all users)"""
        try:
            current_user_id = int(get_jwt_identity())
            anomaly = Anomaly.query.get(anomaly_id)
            
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            anomaly.approve_predictions(current_user_id)
            db.session.commit()
            
            return {
                "message": "Anomaly predictions approved successfully",
                "anomaly": anomaly.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class AnomalyPredictionEditAPI(Resource):
    @jwt_required()
    def put(self, anomaly_id):
        """Edit an anomaly's predictions manually (accessible to all users)"""
        try:
            current_user_id = int(get_jwt_identity())
            anomaly = Anomaly.query.get(anomaly_id)
            
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            # Extract prediction values
            predictions = data.get('predictions', {})
            
            # Validate prediction values
            valid_fields = ['fiabilite_integrite', 'disponibilite', 'process_safety', 'criticite']
            prediction_data = {}
            
            for field in valid_fields:
                if field in predictions:
                    try:
                        prediction_data[field] = float(predictions[field])
                    except (ValueError, TypeError):
                        return {"error": f"Invalid value for {field}, must be a number"}, 400
            
            if not prediction_data:
                return {"error": "No valid prediction fields provided"}, 400
            
            # Update predictions manually (this will auto-approve)
            anomaly.update_manual_predictions(current_user_id, **prediction_data)
            db.session.commit()
            
            return {
                "message": "Predictions updated and approved successfully",
                "anomaly": anomaly.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# Create the Blueprint and API objects
anomalies_bp = Blueprint('anomalies_api', __name__)
api = Api(anomalies_bp)

# Register the resources with the API
api.add_resource(AnomalyListAPI, '')
api.add_resource(AnomalyAPI, '/<int:anomaly_id>')
api.add_resource(FileAnomalyAPI, '/<int:anomaly_id>/close')
