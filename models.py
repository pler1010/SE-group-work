from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='passenger')  # 'driver' or 'passenger'
    
    preferences = db.relationship('UserPreference', backref='user', lazy=True)
    logs = db.relationship('InteractionLog', backref='user', lazy=True)
    
    def has_permission(self, action):
        if self.role == 'driver':
            return True
        else:
            permissions = Permission.query.filter_by(role='passenger').first()
            if not permissions:
                return False
            return getattr(permissions, action, False)
    
    # 为了兼容现有代码，保留这些属性
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return str(self.id)

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    preference_type = db.Column(db.String(50), nullable=False)  # 'voice', 'gesture', 'visual'
    preference_key = db.Column(db.String(100), nullable=False)
    preference_value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InteractionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    interaction_type = db.Column(db.String(50), nullable=False)  # 'voice', 'gesture', 'visual'
    action = db.Column(db.String(200), nullable=False)
    success = db.Column(db.Boolean, default=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), unique=True, nullable=False)
    control_ac = db.Column(db.Boolean, default=False)
    control_music = db.Column(db.Boolean, default=True)
    control_navigation = db.Column(db.Boolean, default=False)
    system_settings = db.Column(db.Boolean, default=False)
