# maintenance_api.py
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, MaintenanceWindow, Anomaly, ActionPlan, ActionItem
from datetime import datetime, timedelta

class MaintenanceWindowAPI(Resource):
    @jwt_required()
    def get(self, window_id=None):
        """Get a specific maintenance window or all maintenance windows"""
        try:
            if window_id:
                # Get specific window
                window = MaintenanceWindow.query.get(window_id)
                if not window:
                    return {"error": "Maintenance window not found"}, 404
                
                return {"maintenance_window": window.to_dict()}, 200
            else:
                # Get all windows with pagination
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 20, type=int)
                
                # Get filter parameters
                start_date = request.args.get('start_date', None)
                end_date = request.args.get('end_date', None)
                status = request.args.get('status', None)
                type_filter = request.args.get('type', None)
                
                # Base query
                query = MaintenanceWindow.query
                
                # Apply filters
                if start_date:
                    try:
                        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        query = query.filter(MaintenanceWindow.start_date >= start)
                    except:
                        pass
                
                if end_date:
                    try:
                        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        query = query.filter(MaintenanceWindow.end_date <= end)
                    except:
                        pass
                
                if status:
                    query = query.filter(MaintenanceWindow.status == status)
                
                if type_filter:
                    query = query.filter(MaintenanceWindow.type == type_filter)
                
                # Order by start date
                query = query.order_by(MaintenanceWindow.start_date.asc())
                
                # Execute query with pagination
                windows = query.paginate(page=page, per_page=per_page, error_out=False)
                
                return {
                    "maintenance_windows": [window.to_dict() for window in windows.items],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": windows.total,
                        "pages": windows.pages
                    }
                }, 200
                
        except Exception as e:
            return {"error": str(e)}, 500
    
    @jwt_required()
    def post(self):
        """Create a new maintenance window"""
        try:
            current_user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            # Validate required fields
            required_fields = ["type", "duration_days", "start_date", "description"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {"error": f"Missing required fields: {missing_fields}"}, 400
            
            # Parse dates
            try:
                start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            except:
                return {"error": "Invalid start_date format. Use ISO format."}, 400
            
            # Calculate end date
            end_date = start_date + timedelta(days=int(data['duration_days']))
            
            # Create maintenance window
            window = MaintenanceWindow(
                type=data['type'],
                duration_days=data['duration_days'],
                start_date=start_date,
                end_date=end_date,
                description=data['description'],
                status=data.get('status', 'scheduled'),
                created_by_user_id=current_user_id
            )
            
            db.session.add(window)
            db.session.commit()
            
            return {
                "message": "Maintenance window created successfully",
                "maintenance_window": window.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def put(self, window_id):
        """Update a maintenance window"""
        try:
            current_user_id = int(get_jwt_identity())
            window = MaintenanceWindow.query.get(window_id)
            
            if not window:
                return {"error": "Maintenance window not found"}, 404
            
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            # Update fields
            updatable_fields = ['type', 'description', 'status']
            for field in updatable_fields:
                if field in data:
                    setattr(window, field, data[field])
            
            # Update dates if provided
            if 'start_date' in data:
                try:
                    window.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
                except:
                    return {"error": "Invalid start_date format. Use ISO format."}, 400
            
            # Update duration and end date
            if 'duration_days' in data:
                window.duration_days = data['duration_days']
                window.end_date = window.start_date + timedelta(days=int(data['duration_days']))
            
            window.updated_by_user_id = current_user_id
            db.session.commit()
            
            return {
                "message": "Maintenance window updated successfully",
                "maintenance_window": window.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def delete(self, window_id):
        """Delete a maintenance window"""
        try:
            window = MaintenanceWindow.query.get(window_id)
            
            if not window:
                return {"error": "Maintenance window not found"}, 404
            
            # Check if window has scheduled anomalies
            if window.scheduled_anomalies:
                return {"error": "Cannot delete maintenance window with scheduled anomalies"}, 400
            
            db.session.delete(window)
            db.session.commit()
            
            return {"message": "Maintenance window deleted successfully"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class ScheduleAnomalyAPI(Resource):
    @jwt_required()
    def post(self, window_id):
        """Schedule an anomaly to a maintenance window"""
        try:
            current_user_id = int(get_jwt_identity())
            window = MaintenanceWindow.query.get(window_id)
            
            if not window:
                return {"error": "Maintenance window not found"}, 404
            
            data = request.get_json()
            if not data or 'anomaly_id' not in data:
                return {"error": "Anomaly ID is required"}, 400
            
            anomaly_id = data['anomaly_id']
            anomaly = Anomaly.query.get(anomaly_id)
            
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            # Schedule anomaly to window
            anomaly.maintenance_window_id = window_id
            anomaly.updated_by_user_id = current_user_id
            anomaly.updated_at = datetime.utcnow()
            
            # Update status if specified
            if 'status' in data:
                valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
                if data['status'] in valid_statuses:
                    anomaly.status = data['status']
            
            db.session.commit()
            
            return {
                "message": "Anomaly scheduled to maintenance window successfully",
                "anomaly": anomaly.to_dict(),
                "maintenance_window": window.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class ActionPlanAPI(Resource):
    @jwt_required()
    def get(self, anomaly_id=None):
        """Get action plan for an anomaly"""
        try:
            if not anomaly_id:
                return {"error": "Anomaly ID is required"}, 400
            
            # Check if anomaly exists
            anomaly = Anomaly.query.get(anomaly_id)
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            # Get action plan
            action_plan = ActionPlan.query.filter_by(anomaly_id=anomaly_id).first()
            if not action_plan:
                return {"error": "No action plan found for this anomaly"}, 404
            
            return {"action_plan": action_plan.to_dict()}, 200
            
        except Exception as e:
            return {"error": str(e)}, 500
    
    @jwt_required()
    def post(self, anomaly_id=None):
        """Create a new action plan for an anomaly"""
        try:
            current_user_id = int(get_jwt_identity())
            
            if not anomaly_id:
                return {"error": "Anomaly ID is required"}, 400
            
            # Check if anomaly exists
            anomaly = Anomaly.query.get(anomaly_id)
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            # Check if action plan already exists
            existing_plan = ActionPlan.query.filter_by(anomaly_id=anomaly_id).first()
            if existing_plan:
                return {"error": "Action plan already exists for this anomaly"}, 400
            
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            # Create action plan
            action_plan = ActionPlan(
                anomaly_id=anomaly_id,
                needs_outage=data.get('needs_outage', False),
                outage_type=data.get('outage_type'),
                outage_duration=data.get('outage_duration'),
                planned_date=datetime.fromisoformat(data['planned_date'].replace('Z', '+00:00')) if 'planned_date' in data else None,
                total_duration_hours=data.get('total_duration_hours'),
                total_duration_days=data.get('total_duration_days'),
                estimated_cost=data.get('estimated_cost'),
                priority=data.get('priority'),
                comments=data.get('comments'),
                status='draft',
                created_by_user_id=current_user_id
            )
            
            # Add action items if provided
            if 'action_items' in data and isinstance(data['action_items'], list):
                for item_data in data['action_items']:
                    action_item = ActionItem(
                        action=item_data.get('action', ''),
                        responsable=item_data.get('responsable'),
                        pdrs_disponible=item_data.get('pdrs_disponible', True),
                        ressources_internes=item_data.get('ressources_internes'),
                        ressources_externes=item_data.get('ressources_externes'),
                        statut=item_data.get('statut', 'pending'),
                        duree_heures=item_data.get('duree_heures'),
                        duree_jours=item_data.get('duree_jours'),
                        created_by_user_id=current_user_id
                    )
                    action_plan.action_items.append(action_item)
            
            db.session.add(action_plan)
            db.session.commit()
            
            return {
                "message": "Action plan created successfully",
                "action_plan": action_plan.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def put(self, anomaly_id=None):
        """Update an action plan for an anomaly"""
        try:
            current_user_id = int(get_jwt_identity())
            
            if not anomaly_id:
                return {"error": "Anomaly ID is required"}, 400
            
            # Check if action plan exists
            action_plan = ActionPlan.query.filter_by(anomaly_id=anomaly_id).first()
            if not action_plan:
                return {"error": "No action plan found for this anomaly"}, 404
            
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            # Update fields
            updatable_fields = [
                'needs_outage', 'outage_type', 'outage_duration', 'total_duration_hours',
                'total_duration_days', 'estimated_cost', 'priority', 'comments', 'status'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(action_plan, field, data[field])
            
            # Update planned date if provided
            if 'planned_date' in data:
                try:
                    action_plan.planned_date = datetime.fromisoformat(data['planned_date'].replace('Z', '+00:00'))
                except:
                    return {"error": "Invalid planned_date format. Use ISO format."}, 400
            
            # Update action items if provided
            if 'action_items' in data and isinstance(data['action_items'], list):
                # Process existing items (update or delete)
                existing_item_ids = set()
                for item_data in data['action_items']:
                    if 'id' in item_data:
                        item_id = item_data['id']
                        existing_item_ids.add(item_id)
                        
                        # Update existing item
                        item = ActionItem.query.get(item_id)
                        if item and item.action_plan_id == action_plan.id:
                            for field in ['action', 'responsable', 'pdrs_disponible', 
                                          'ressources_internes', 'ressources_externes', 
                                          'statut', 'duree_heures', 'duree_jours']:
                                if field in item_data:
                                    setattr(item, field, item_data[field])
                            item.updated_by_user_id = current_user_id
                    else:
                        # Create new item
                        new_item = ActionItem(
                            action_plan_id=action_plan.id,
                            action=item_data.get('action', ''),
                            responsable=item_data.get('responsable'),
                            pdrs_disponible=item_data.get('pdrs_disponible', True),
                            ressources_internes=item_data.get('ressources_internes'),
                            ressources_externes=item_data.get('ressources_externes'),
                            statut=item_data.get('statut', 'pending'),
                            duree_heures=item_data.get('duree_heures'),
                            duree_jours=item_data.get('duree_jours'),
                            created_by_user_id=current_user_id
                        )
                        db.session.add(new_item)
                
                # Delete items not in the update
                for item in action_plan.action_items:
                    if item.id not in existing_item_ids:
                        db.session.delete(item)
            
            action_plan.updated_by_user_id = current_user_id
            db.session.commit()
            
            return {
                "message": "Action plan updated successfully",
                "action_plan": action_plan.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class ActionItemAPI(Resource):
    @jwt_required()
    def post(self, action_plan_id):
        """Add a new action item to an action plan"""
        try:
            current_user_id = int(get_jwt_identity())
            
            # Check if action plan exists
            action_plan = ActionPlan.query.get(action_plan_id)
            if not action_plan:
                return {"error": "Action plan not found"}, 404
            
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            # Create new action item
            action_item = ActionItem(
                action_plan_id=action_plan_id,
                action=data.get('action', ''),
                responsable=data.get('responsable'),
                pdrs_disponible=data.get('pdrs_disponible', True),
                ressources_internes=data.get('ressources_internes'),
                ressources_externes=data.get('ressources_externes'),
                statut=data.get('statut', 'pending'),
                duree_heures=data.get('duree_heures'),
                duree_jours=data.get('duree_jours'),
                created_by_user_id=current_user_id
            )
            
            db.session.add(action_item)
            db.session.commit()
            
            return {
                "message": "Action item created successfully",
                "action_item": action_item.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def put(self, action_plan_id, item_id):
        """Update an action item"""
        try:
            current_user_id = int(get_jwt_identity())
            
            # Check if action item exists and belongs to the specified action plan
            action_item = ActionItem.query.filter_by(id=item_id, action_plan_id=action_plan_id).first()
            if not action_item:
                return {"error": "Action item not found"}, 404
            
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            # Update fields
            updatable_fields = [
                'action', 'responsable', 'pdrs_disponible', 'ressources_internes',
                'ressources_externes', 'statut', 'duree_heures', 'duree_jours'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(action_item, field, data[field])
            
            action_item.updated_by_user_id = current_user_id
            db.session.commit()
            
            return {
                "message": "Action item updated successfully",
                "action_item": action_item.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def delete(self, action_plan_id, item_id):
        """Delete an action item"""
        try:
            # Check if action item exists and belongs to the specified action plan
            action_item = ActionItem.query.filter_by(id=item_id, action_plan_id=action_plan_id).first()
            if not action_item:
                return {"error": "Action item not found"}, 404
            
            db.session.delete(action_item)
            db.session.commit()
            
            return {"message": "Action item deleted successfully"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
