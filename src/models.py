from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class EmergencyReport(db.Model):
    __tablename__ = 'emergency_reports'  # This is where chat emergency reports are stored
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    description = db.Column(db.Text)
    audio_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact': self.contact,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'description': self.description,
            'audio_filename': self.audio_filename,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }



class EmergencyService(db.Model):
    __tablename__ = 'emergency_service'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False)  # Required city field
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'service_type': self.service_type,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }