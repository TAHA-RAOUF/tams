# app/api/v1/endpoints/action_plans.py
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.models import db, ActionPlan, ActionItem, Anomaly

class ActionPlanAPI(Resource):
    @jwt_required()
    def get(self, anomaly_id):
        """Get action plan for an anomaly"""
        try:
            # Verify anomaly exists
            anomaly = Anomaly.query.get(anomaly_id)
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            # Get existing action plan
            action_plan = ActionPlan.query.filter_by(anomaly_id=anomaly_id).first()
            if not action_plan:
                return {"error": "No action plan found for this anomaly"}, 404
            
            return {"action_plan": action_plan.to_dict()}, 200
            
        except Exception as e:
            return {"error": str(e)}, 500
    
    @jwt_required()
    def post(self, anomaly_id):
        """Create action plan for an anomaly"""
        try:
            current_user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            # Verify anomaly exists
            anomaly = Anomaly.query.get(anomaly_id)
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            # Check if action plan already exists
            existing_plan = ActionPlan.query.filter_by(anomaly_id=anomaly_id).first()
            if existing_plan:
                return {"error": "Action plan already exists for this anomaly"}, 409
            
            # Create new action plan
            action_plan = ActionPlan(
                anomaly_id=anomaly_id,
                needs_outage=data.get('needs_outage', False),
                outage_type=data.get('outage_type'),
                outage_duration=data.get('outage_duration'),
                planned_date=datetime.fromisoformat(data['planned_date']) if data.get('planned_date') else None,
                total_duration_hours=data.get('total_duration_hours'),
                total_duration_days=data.get('total_duration_days'),
                estimated_cost=data.get('estimated_cost'),
                priority=data.get('priority'),
                comments=data.get('comments'),
                status='draft',
                created_by_user_id=current_user_id,
                updated_by_user_id=current_user_id
            )
            
            db.session.add(action_plan)
            db.session.commit()
            
            return {"message": "Action plan created", "action_plan": action_plan.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def put(self, anomaly_id):
        """Update action plan"""
        try:
            current_user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            # Verify anomaly exists
            anomaly = Anomaly.query.get(anomaly_id)
            if not anomaly:
                return {"error": "Anomaly not found"}, 404
            
            # Get existing action plan
            action_plan = ActionPlan.query.filter_by(anomaly_id=anomaly_id).first()
            if not action_plan:
                return {"error": "Action plan not found"}, 404
            
            # Update fields
            if 'needs_outage' in data:
                action_plan.needs_outage = data['needs_outage']
            if 'outage_type' in data:
                action_plan.outage_type = data['outage_type']
            if 'outage_duration' in data:
                action_plan.outage_duration = data['outage_duration']
            if 'planned_date' in data:
                action_plan.planned_date = datetime.fromisoformat(data['planned_date']) if data['planned_date'] else None
            if 'total_duration_hours' in data:
                action_plan.total_duration_hours = data['total_duration_hours']
            if 'total_duration_days' in data:
                action_plan.total_duration_days = data['total_duration_days']
            if 'estimated_cost' in data:
                action_plan.estimated_cost = data['estimated_cost']
            if 'priority' in data:
                action_plan.priority = data['priority']
            if 'comments' in data:
                action_plan.comments = data['comments']
            if 'status' in data:
                action_plan.status = data['status']
            
            # Update metadata
            action_plan.updated_at = datetime.utcnow()
            action_plan.updated_by_user_id = current_user_id
            
            db.session.commit()
            
            return {"message": "Action plan updated", "action_plan": action_plan.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class ActionItemAPI(Resource):
    @jwt_required()
    def post(self, action_plan_id):
        """Add action item to action plan"""
        try:
            current_user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            # Verify action plan exists
            action_plan = ActionPlan.query.get(action_plan_id)
            if not action_plan:
                return {"error": "Action plan not found"}, 404
            
            # Create new action item
            action_item = ActionItem(
                action_plan_id=action_plan_id,
                action=data.get('action'),
                responsable=data.get('responsable'),
                pdrs_disponible=data.get('pdrs_disponible', True),
                ressources_internes=data.get('ressources_internes'),
                ressources_externes=data.get('ressources_externes'),
                statut=data.get('statut', 'pending'),
                duree_heures=data.get('duree_heures'),
                duree_jours=data.get('duree_jours'),
                created_by_user_id=current_user_id,
                updated_by_user_id=current_user_id
            )
            
            db.session.add(action_item)
            db.session.commit()
            
            return {"message": "Action item added", "action_item": action_item.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def put(self, action_plan_id, item_id):
        """Update action item"""
        try:
            current_user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return {"error": "No data provided"}, 400
            
            # Verify action item exists
            action_item = ActionItem.query.filter_by(id=item_id, action_plan_id=action_plan_id).first()
            if not action_item:
                return {"error": "Action item not found"}, 404
            
            # Update fields
            if 'action' in data:
                action_item.action = data['action']
            if 'responsable' in data:
                action_item.responsable = data['responsable']
            if 'pdrs_disponible' in data:
                action_item.pdrs_disponible = data['pdrs_disponible']
            if 'ressources_internes' in data:
                action_item.ressources_internes = data['ressources_internes']
            if 'ressources_externes' in data:
                action_item.ressources_externes = data['ressources_externes']
            if 'statut' in data:
                action_item.statut = data['statut']
            if 'duree_heures' in data:
                action_item.duree_heures = data['duree_heures']
            if 'duree_jours' in data:
                action_item.duree_jours = data['duree_jours']
            
            # Update metadata
            action_item.updated_at = datetime.utcnow()
            action_item.updated_by_user_id = current_user_id
            
            db.session.commit()
            
            return {"message": "Action item updated", "action_item": action_item.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
    
    @jwt_required()
    def delete(self, action_plan_id, item_id):
        """Delete action item"""
        try:
            # Verify action item exists
            action_item = ActionItem.query.filter_by(id=item_id, action_plan_id=action_plan_id).first()
            if not action_item:
                return {"error": "Action item not found"}, 404
            
            db.session.delete(action_item)
            db.session.commit()
            
            return {"message": "Action item deleted"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
