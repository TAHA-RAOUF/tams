# action_plan.py - Action Plan and Action Item models
from app.models import db
from datetime import datetime

class ActionPlan(db.Model):
    __tablename__ = 'action_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    anomaly_id = db.Column(db.Integer, db.ForeignKey('anomalies.id'), nullable=False, unique=True)
    
    # Planning details
    needs_outage = db.Column(db.Boolean, default=False, nullable=False)
    outage_type = db.Column(db.String(50), nullable=True)  # planned, emergency
    outage_duration = db.Column(db.Integer, nullable=True)  # in hours
    planned_date = db.Column(db.DateTime, nullable=True)
    total_duration_hours = db.Column(db.Float, nullable=True)
    total_duration_days = db.Column(db.Float, nullable=True)
    estimated_cost = db.Column(db.Float, nullable=True)
    priority = db.Column(db.String(20), nullable=True)  # low, medium, high, critical
    comments = db.Column(db.Text, nullable=True)
    
    # Status tracking
    status = db.Column(db.String(20), default='draft', nullable=False)  # draft, approved, in_progress, completed
    
    # Metadata
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    anomaly = db.relationship('Anomaly', backref=db.backref('action_plan', uselist=False))
    created_by = db.relationship('User', foreign_keys=[created_by_user_id], backref='created_action_plans')
    updated_by = db.relationship('User', foreign_keys=[updated_by_user_id], backref='updated_action_plans')
    approved_by = db.relationship('User', foreign_keys=[approved_by_user_id], backref='approved_action_plans')
    
    def to_dict(self):
        return {
            'id': self.id,
            'anomaly_id': self.anomaly_id,
            'needs_outage': self.needs_outage,
            'outage_type': self.outage_type,
            'outage_duration': self.outage_duration,
            'planned_date': self.planned_date.isoformat() if self.planned_date else None,
            'total_duration_hours': self.total_duration_hours,
            'total_duration_days': self.total_duration_days,
            'estimated_cost': self.estimated_cost,
            'priority': self.priority,
            'comments': self.comments,
            'status': self.status,
            'created_by_user_id': self.created_by_user_id,
            'updated_by_user_id': self.updated_by_user_id,
            'approved_by_user_id': self.approved_by_user_id,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'action_items': [item.to_dict() for item in self.action_items]
        }


class ActionItem(db.Model):
    __tablename__ = 'action_items'
    
    id = db.Column(db.Integer, primary_key=True)
    action_plan_id = db.Column(db.Integer, db.ForeignKey('action_plans.id'), nullable=False)
    
    # Action details
    action = db.Column(db.Text, nullable=False)
    responsable = db.Column(db.String(100), nullable=True)
    pdrs_disponible = db.Column(db.Boolean, default=True, nullable=False)  # Parts/pieces available
    ressources_internes = db.Column(db.String(200), nullable=True)  # Internal resources
    ressources_externes = db.Column(db.String(200), nullable=True)  # External resources
    statut = db.Column(db.String(20), default='pending', nullable=False)  # pending, in_progress, completed, blocked
    duree_heures = db.Column(db.Float, nullable=True)  # Duration in hours
    duree_jours = db.Column(db.Float, nullable=True)  # Duration in days
    
    # Metadata
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    action_plan = db.relationship('ActionPlan', backref='action_items')
    created_by = db.relationship('User', foreign_keys=[created_by_user_id], backref='created_action_items')
    updated_by = db.relationship('User', foreign_keys=[updated_by_user_id], backref='updated_action_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'action_plan_id': self.action_plan_id,
            'action': self.action,
            'responsable': self.responsable,
            'pdrs_disponible': self.pdrs_disponible,
            'ressources_internes': self.ressources_internes,
            'ressources_externes': self.ressources_externes,
            'statut': self.statut,
            'duree_heures': self.duree_heures,
            'duree_jours': self.duree_jours,
            'created_by_user_id': self.created_by_user_id,
            'updated_by_user_id': self.updated_by_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
