# import_api.py
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Anomaly
from app.core.predictor import EquipmentReliabilityPredictor
from datetime import datetime
import pandas as pd
import io
import os
import tempfile

class ImportAnomaliesAPI(Resource):
    @jwt_required()
    def post(self):
        """Import anomalies from CSV or Excel file"""
        try:
            current_user_id = int(get_jwt_identity())
            
            # Check if file is in the request
            if 'file' not in request.files:
                return {"error": "No file provided"}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {"error": "No file selected"}, 400
            
            # Save the file temporarily
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file.save(temp_file.name)
            temp_file.close()
            
            # Read file based on extension
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(temp_file.name)
                elif file.filename.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(temp_file.name)
                else:
                    os.unlink(temp_file.name)
                    return {"error": "File must be CSV or Excel format"}, 400
            except Exception as e:
                os.unlink(temp_file.name)
                return {"error": f"Error reading file: {str(e)}"}, 400
            
            # Delete temporary file
            os.unlink(temp_file.name)
            
            # Map columns to model fields
            column_mapping = {
                # Required fields with potential variations in naming
                "Num_equipement": ["Num_equipement", "Num equipement", "Equipment ID", "EquipmentID"],
                "Systeme": ["Systeme", "Système", "System"],
                "Description": ["Description", "Description anomaly", "Anomaly description"],
                "Date de détéction de l'anomalie": ["Date de détéction de l'anomalie", "Detection date", "Date"],
                "Description de l'équipement": ["Description de l'équipement", "Equipment description"],
                "Section propriétaire": ["Section propriétaire", "Owner section", "Section"]
            }
            
            # Try to find matching columns in the file
            field_mapping = {}
            for target_field, possible_names in column_mapping.items():
                for name in possible_names:
                    if name in df.columns:
                        field_mapping[target_field] = name
                        break
            
            # Check if all required fields are mapped
            missing_fields = [field for field in column_mapping.keys() if field not in field_mapping]
            if missing_fields:
                return {
                    "error": f"Missing required columns: {missing_fields}",
                    "found_columns": list(df.columns),
                    "mapping_needed": missing_fields
                }, 400
            
            # Fill missing values to avoid errors
            df = df.fillna("unknown")
            
            # Initialize predictor
            predictor = EquipmentReliabilityPredictor()
            
            # Process records
            results = {
                "total_rows": len(df),
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            created_anomalies = []
            
            for idx, row in df.iterrows():
                try:
                    # Parse date
                    date_str = row[field_mapping["Date de détéction de l'anomalie"]]
                    try:
                        date_detection = pd.to_datetime(date_str)
                    except:
                        # If we can't parse the date, add an error and skip this row
                        results["errors"].append(f"Row {idx+1}: Invalid date format '{date_str}'")
                        results["failed"] += 1
                        continue
                    
                    # Create anomaly record
                    anomaly = Anomaly(
                        num_equipement=str(row[field_mapping["Num_equipement"]]),
                        systeme=str(row[field_mapping["Systeme"]]),
                        description=str(row[field_mapping["Description"]]),
                        date_detection=date_detection,
                        description_equipement=str(row[field_mapping["Description de l'équipement"]]),
                        section_proprietaire=str(row[field_mapping["Section propriétaire"]]),
                        created_by_user_id=current_user_id
                    )
                    
                    # Make prediction
                    try:
                        prediction_input = {
                            "Num_equipement": str(row[field_mapping["Num_equipement"]]),
                            "Systeme": str(row[field_mapping["Systeme"]]),
                            "Description": str(row[field_mapping["Description"]])
                        }
                        predictions = predictor.predict_single(prediction_input)
                        anomaly.update_predictions(predictions)
                    except Exception as e:
                        # Log prediction error but continue with import
                        results["errors"].append(f"Row {idx+1}: Prediction error: {str(e)}")
                    
                    db.session.add(anomaly)
                    created_anomalies.append(anomaly)
                    results["successful"] += 1
                    
                except Exception as e:
                    results["errors"].append(f"Row {idx+1}: {str(e)}")
                    results["failed"] += 1
            
            # Commit all valid records
            db.session.commit()
            
            # Add sample of imported anomalies to the results
            sample_size = min(10, len(created_anomalies))
            results["sample_anomalies"] = [anomaly.to_dict() for anomaly in created_anomalies[:sample_size]]
            
            return {
                "message": f"Imported {results['successful']} anomalies successfully",
                "import_results": results
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Import failed: {str(e)}"}, 500
