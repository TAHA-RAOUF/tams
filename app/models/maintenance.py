# maintenance.py - Maintenance Window model
from app.models import db
from datetime import datetime

class MaintenanceWindow(db.Model):
    __tablename__ = 'maintenance_windows'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # planned, emergency, routine
    duration_days = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='scheduled', nullable=False)  # scheduled, in_progress, completed, cancelled
    
    # Metadata
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_user_id], backref='created_maintenance_windows')
    updated_by = db.relationship('User', foreign_keys=[updated_by_user_id], backref='updated_maintenance_windows')
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'duration_days': self.duration_days,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'status': self.status,
            'created_by_user_id': self.created_by_user_id,
            'updated_by_user_id': self.updated_by_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'scheduled_anomalies_count': len(self.scheduled_anomalies)
        }
