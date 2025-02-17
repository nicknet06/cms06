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

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('emergency_service.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(50), nullable=False)  # new, good, needs maintenance, out of service
    last_maintenance = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'quantity': self.quantity,
            'available': self.available,
            'condition': self.condition,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None
        }

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('emergency_service.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    plate_number = db.Column(db.String(20), nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False)  # available, in-use, maintenance, out-of-service
    capacity = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'model': self.model,
            'plate_number': self.plate_number,
            'status': self.status,
            'capacity': self.capacity
        }

class Personnel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('emergency_service.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    speciality = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=False)  # on-duty, off-duty, on-leave
    shift = db.Column(db.String(20), nullable=False)  # morning, evening, night
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'speciality': self.speciality,
            'status': self.status,
            'shift': self.shift
        }

class ResourceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('emergency_service.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=True)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnel.id'), nullable=True)
    requester = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # pending, approved, rejected, completed
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'requester': self.requester,
            'purpose': self.purpose,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }