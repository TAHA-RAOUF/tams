# anomaly_status_api.py
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Anomaly
from datetime import datetime

class AnomalyStatusAPI(Resource):
    @jwt_required()
    def put(self, anomaly_id):
        """Update an anomaly's status with proper flow transition"""
        try:
            current_user_id = int(get_jwt_identity())
            anomaly = Anomaly.query.get(anomaly_id)
            
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            data = request.get_json()
            if not data or 'status' not in data:
                return {"error": "Status is required"}, 400
            
            new_status = data['status']
            current_status = anomaly.status
            
            # Define valid status transitions
            valid_transitions = {
                'open': ['in_progress', 'closed'],  # Can go from open to in_progress or directly to closed
                'in_progress': ['resolved', 'closed'],  # From in_progress, can resolve or close
                'resolved': ['closed', 'in_progress'],  # From resolved, can close or reopen as in_progress
                'closed': ['open']  # Can reopen a closed anomaly
            }
            
            # Check if the transition is valid
            if new_status not in valid_transitions.get(current_status, []):
                return {
                    "error": f"Invalid status transition from '{current_status}' to '{new_status}'",
                    "valid_transitions": valid_transitions.get(current_status, [])
                }, 400
            
            # Update status
            anomaly.status = new_status
            anomaly.updated_at = datetime.utcnow()
            anomaly.updated_by_user_id = current_user_id
            anomaly.last_modified_by = current_user_id
            anomaly.last_modified_at = datetime.utcnow()
            
            # Add comments if provided
            if 'comments' in data:
                # We could add a new table for status change comments/history
                # For now, we'll just update the description with a timestamp
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
                status_note = f"\n[{timestamp}] Status changed from {current_status} to {new_status}: {data['comments']}"
                
                if anomaly.description:
                    anomaly.description += status_note
                else:
                    anomaly.description = status_note
            
            db.session.commit()
            
            return {
                "message": f"Anomaly status updated from '{current_status}' to '{new_status}'",
                "anomaly": anomaly.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class AnomalyBulkStatusAPI(Resource):
    @jwt_required()
    def put(self):
        """Update multiple anomalies' statuses at once"""
        try:
            current_user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data or 'anomalies' not in data or 'status' not in data:
                return {"error": "Anomaly IDs and target status are required"}, 400
            
            anomaly_ids = data['anomalies']
            if not isinstance(anomaly_ids, list) or not anomaly_ids:
                return {"error": "Anomaly IDs must be a non-empty list"}, 400
                
            new_status = data['status']
            if new_status not in ['open', 'in_progress', 'resolved', 'closed']:
                return {"error": "Invalid status value"}, 400
            
            # Get all anomalies in one query
            anomalies = Anomaly.query.filter(Anomaly.id.in_(anomaly_ids)).all()
            found_ids = [a.id for a in anomalies]
            missing_ids = [aid for aid in anomaly_ids if aid not in found_ids]
            
            results = {
                "updated": [],
                "skipped": [],
                "not_found": missing_ids
            }
            
            # Define valid status transitions
            valid_transitions = {
                'open': ['in_progress', 'closed'],
                'in_progress': ['resolved', 'closed'],
                'resolved': ['closed', 'in_progress'],
                'closed': ['open']
            }
            
            # Update each anomaly
            for anomaly in anomalies:
                current_status = anomaly.status
                
                # Check if transition is valid
                if new_status in valid_transitions.get(current_status, []):
                    # Update status
                    anomaly.status = new_status
                    anomaly.updated_at = datetime.utcnow()
                    anomaly.updated_by_user_id = current_user_id
                    anomaly.last_modified_by = current_user_id
                    anomaly.last_modified_at = datetime.utcnow()
                    
                    # Add to results
                    results["updated"].append({
                        "id": anomaly.id,
                        "from_status": current_status,
                        "to_status": new_status
                    })
                else:
                    # Skip invalid transitions
                    results["skipped"].append({
                        "id": anomaly.id,
                        "current_status": current_status,
                        "valid_transitions": valid_transitions.get(current_status, [])
                    })
            
            # Commit changes for all valid updates
            db.session.commit()
            
            return {
                "message": f"Updated {len(results['updated'])} anomalies to '{new_status}' status",
                "results": results
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
