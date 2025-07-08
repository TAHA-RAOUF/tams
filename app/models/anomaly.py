# anomaly.py - Anomaly model
from app.models import db
from datetime import datetime

class Anomaly(db.Model):
    __tablename__ = 'anomalies'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic anomaly information
    title = db.Column(db.String(200), nullable=False)  # Human-readable title
    description = db.Column(db.Text, nullable=False)
    num_equipement = db.Column(db.String(50), nullable=False)  # Equipment ID
    systeme = db.Column(db.String(50), nullable=False)  # System type
    equipment_id = db.Column(db.String(100), nullable=True)  # Additional equipment reference
    service = db.Column(db.String(100), nullable=True)  # Service department
    responsible_person = db.Column(db.String(100), nullable=True)  # Person responsible
    status = db.Column(db.String(20), default='open', nullable=False)  # open, in_progress, resolved, closed
    origin_source = db.Column(db.String(50), nullable=True)  # inspection, maintenance, operation, etc.
    
    # Original fields for compatibility
    date_detection = db.Column(db.DateTime, nullable=False)
    description_equipement = db.Column(db.String(255), nullable=False)
    section_proprietaire = db.Column(db.String(10), nullable=False)
    
    # AI prediction scores
    fiabilite_score = db.Column(db.Float, nullable=True)
    integrite_score = db.Column(db.Float, nullable=True)
    disponibilite_score = db.Column(db.Float, nullable=True)
    process_safety_score = db.Column(db.Float, nullable=True)
    criticality_level = db.Column(db.Float, nullable=True)
    
    # User override scores
    user_fiabilite_score = db.Column(db.Float, nullable=True)
    user_integrite_score = db.Column(db.Float, nullable=True)
    user_disponibilite_score = db.Column(db.Float, nullable=True)
    user_process_safety_score = db.Column(db.Float, nullable=True)
    user_criticality_level = db.Column(db.Float, nullable=True)
    use_user_scores = db.Column(db.Boolean, default=False, nullable=False)
    
    # Planning and maintenance
    estimated_hours = db.Column(db.Float, nullable=True)
    priority = db.Column(db.String(20), nullable=True)  # low, medium, high, critical
    maintenance_window_id = db.Column(db.Integer, db.ForeignKey('maintenance_windows.id'), nullable=True)
    
    # Approval status and tracking
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # REX file S3 URL
    rex_file = db.Column(db.String(512), nullable=True)  # S3 URL or key
    
    # Metadata - track who created and last updated
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    last_modified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    last_modified_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    approved_by = db.relationship('User', foreign_keys=[approved_by_user_id], backref='approved_anomalies')
    created_by = db.relationship('User', foreign_keys=[created_by_user_id], backref='created_anomalies')
    updated_by = db.relationship('User', foreign_keys=[updated_by_user_id], backref='updated_anomalies')
    last_modified_by_user = db.relationship('User', foreign_keys=[last_modified_by], backref='last_modified_anomalies')
    maintenance_window = db.relationship('MaintenanceWindow', backref='scheduled_anomalies')
    
    def get_active_scores(self):
        """Get the currently active scores (user override or AI prediction)"""
        if self.use_user_scores:
            return {
                'fiabilite_integrite': self.user_fiabilite_score,
                'disponibilite': self.user_disponibilite_score,
                'process_safety': self.user_process_safety_score,
                'criticite': self.user_criticality_level
            }
        else:
            return {
                'fiabilite_integrite': self.fiabilite_score,
                'disponibilite': self.disponibilite_score,
                'process_safety': self.process_safety_score,
                'criticite': self.criticality_level
            }
    
    def to_dict(self):
        active_scores = self.get_active_scores()
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'num_equipement': self.num_equipement,
            'systeme': self.systeme,
            'equipment_id': self.equipment_id,
            'service': self.service,
            'responsible_person': self.responsible_person,
            'status': self.status,
            'origin_source': self.origin_source,
            'date_detection': self.date_detection.isoformat() if self.date_detection else None,
            'description_equipement': self.description_equipement,
            'section_proprietaire': self.section_proprietaire,
            'ai_predictions': {
                'fiabilite_score': self.fiabilite_score,
                'integrite_score': self.integrite_score,
                'disponibilite_score': self.disponibilite_score,
                'process_safety_score': self.process_safety_score,
                'criticality_level': self.criticality_level
            },
            'user_overrides': {
                'fiabilite_score': self.user_fiabilite_score,
                'integrite_score': self.user_integrite_score,
                'disponibilite_score': self.user_disponibilite_score,
                'process_safety_score': self.user_process_safety_score,
                'criticality_level': self.user_criticality_level,
                'use_user_scores': self.use_user_scores
            },
            'active_scores': active_scores,
            'estimated_hours': self.estimated_hours,
            'priority': self.priority,
            'maintenance_window_id': self.maintenance_window_id,
            'is_approved': self.is_approved,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approved_by_user_id': self.approved_by_user_id,
            'created_by_user_id': self.created_by_user_id,
            'updated_by_user_id': self.updated_by_user_id,
            'last_modified_by': self.last_modified_by,
            'last_modified_at': self.last_modified_at.isoformat() if self.last_modified_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'rex_file': self.rex_file
        }
    
    def update_predictions(self, predictions):
        """Update the AI prediction values (backward compatibility)"""
        if isinstance(predictions, dict):
            self.fiabilite_score = float(predictions.get('Fiabilité Intégrité', 0))
            self.disponibilite_score = float(predictions.get('Disponibilité', 0))
            self.process_safety_score = float(predictions.get('Process Safety', 0))
            # Criticality is the sum of all three scores
            self.criticality_level = self.fiabilite_score + self.disponibilite_score + self.process_safety_score
        else:
            # Legacy array format
            self.fiabilite_score = float(predictions[0])
            self.disponibilite_score = float(predictions[1])
            self.process_safety_score = float(predictions[2])
            self.criticality_level = float(predictions[0]) + float(predictions[1]) + float(predictions[2])
        
        self.updated_at = datetime.utcnow()
        # Reset approval when predictions are updated
        self.is_approved = False
        self.approved_at = None
        self.use_user_scores = False  # Use AI scores by default
    
    def approve_predictions(self, user_id):
        """Mark predictions as approved"""
        self.is_approved = True
        self.approved_at = datetime.utcnow()
        self.approved_by_user_id = user_id
        self.updated_at = datetime.utcnow()
        self.updated_by_user_id = user_id
        self.last_modified_by = user_id
        self.last_modified_at = datetime.utcnow()
    
    def update_manual_predictions(self, user_id, fiabilite_score=None, disponibilite_score=None, 
                                process_safety_score=None, criticality_level=None):
        """Update predictions manually and mark as approved"""
        if fiabilite_score is not None:
            self.user_fiabilite_score = float(fiabilite_score)
        if disponibilite_score is not None:
            self.user_disponibilite_score = float(disponibilite_score)
        if process_safety_score is not None:
            self.user_process_safety_score = float(process_safety_score)
        if criticality_level is not None:
            self.user_criticality_level = float(criticality_level)
        else:
            # Recalculate criticality if not provided
            if all(x is not None for x in [self.user_fiabilite_score, self.user_disponibilite_score, self.user_process_safety_score]):
                self.user_criticality_level = self.user_fiabilite_score + self.user_disponibilite_score + self.user_process_safety_score
        
        # Mark to use user scores and approve
        self.use_user_scores = True
        self.is_approved = True
        self.approved_at = datetime.utcnow()
        self.approved_by_user_id = user_id
        self.updated_at = datetime.utcnow()
        self.updated_by_user_id = user_id
        self.last_modified_by = user_id
        self.last_modified_at = datetime.utcnow()
    
    # Backward compatibility properties
    @property
    def fiabilite_integrite(self):
        """Backward compatibility property"""
        return self.user_fiabilite_score if self.use_user_scores else self.fiabilite_score
    
    @fiabilite_integrite.setter
    def fiabilite_integrite(self, value):
        """Backward compatibility setter"""
        if self.use_user_scores:
            self.user_fiabilite_score = value
        else:
            self.fiabilite_score = value
    
    @property
    def disponibilite(self):
        """Backward compatibility property"""
        return self.user_disponibilite_score if self.use_user_scores else self.disponibilite_score
    
    @disponibilite.setter
    def disponibilite(self, value):
        """Backward compatibility setter"""
        if self.use_user_scores:
            self.user_disponibilite_score = value
        else:
            self.disponibilite_score = value
    
    @property
    def process_safety(self):
        """Backward compatibility property"""
        return self.user_process_safety_score if self.use_user_scores else self.process_safety_score
    
    @process_safety.setter
    def process_safety(self, value):
        """Backward compatibility setter"""
        if self.use_user_scores:
            self.user_process_safety_score = value
        else:
            self.process_safety_score = value
    
    @property
    def criticite(self):
        """Backward compatibility property"""
        return self.user_criticality_level if self.use_user_scores else self.criticality_level
    
    @criticite.setter
    def criticite(self, value):
        """Backward compatibility setter"""
        if self.use_user_scores:
            self.user_criticality_level = value
        else:
            self.criticality_level = value
