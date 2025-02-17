from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_cors import CORS
import logging
import os
import time
from datetime import datetime
from sqlalchemy.exc import OperationalError
from models import *

# Import db and models from models.py
from models import db, EmergencyService, EmergencyReport, Equipment, Vehicle, Personnel, ResourceRequest

# Get the absolute path to the directory containing app.py
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'audio_uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize Flask app
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

# Database configuration - Use SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False  # Preserve JSON key order
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize db with app
db.init_app(app)

# Setup logging
logging.basicConfig(
    filename='emergency_reports.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def wait_for_db(retries=5, delay=2):
    with app.app_context():
        for attempt in range(retries):
            try:
                db.create_all()
                print(f"Database connection successful! (Attempt {attempt + 1})")
                print(f"Current time (UTC): 2025-02-17 00:16:55")
                print(f"Current user: nicknet06")
                return True
            except OperationalError as e:
                if attempt == retries - 1:
                    print(f"Could not connect to database after {retries} attempts: {e}")
                    raise
                print(f"Database connection attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
        return False


@app.route('/')
def home():
    return render_template('home.html',
                           current_time="2025-02-17 00:16:55",
                           current_user="nicknet06")


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        try:
            name = request.form.get('name', 'Anonymous')
            contact = request.form.get('contact', 'Not provided')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            description = request.form.get('description')
            audio_filename = request.form.get('audio_filename')

            # Validate that at least one of description or audio_filename is provided
            if not description and not audio_filename:
                raise ValueError("Either description or audio recording is required")

            report = EmergencyReport(
                name=name,
                contact=contact,
                latitude=latitude,
                longitude=longitude,
                description=description,
                audio_filename=audio_filename
            )

            try:
                db.session.add(report)
                db.session.commit()
                logging.info(f"Emergency report saved with ID: {report.id}")
            except Exception as db_error:
                db.session.rollback()
                logging.error(f"Database error: {str(db_error)}")
                raise

            location = f"coordinates: {latitude}, {longitude}" if latitude and longitude else "location pending"

            log_message = f"""
            Emergency Report:
            ID: {report.id}
            Name: {name}
            Contact: {contact}
            Location: {location}
            Description: {description}
            Audio Recording: {audio_filename if audio_filename else 'No audio recorded'}
            Timestamp: {datetime.utcnow()}
            """
            logging.info(log_message)

            response_data = {
                'status': 'success',
                'message': 'Emergency services have been notified.',
                'location': location,
                'eta': '20 minutes'
            }

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(response_data), 200
            else:
                flash('Emergency services have been notified. Help will arrive in 20 minutes.', 'success')
                return redirect(url_for('chat'))

        except ValueError as ve:
            logging.error(f"Validation error: {str(ve)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': str(ve)}), 400
            else:
                flash(str(ve), 'error')
                return redirect(url_for('chat'))
        except Exception as e:
            logging.error(f"Error processing emergency report: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Failed to process emergency report'}), 500
            else:
                flash('Error processing emergency report. Please try again.', 'error')
                return redirect(url_for('chat'))

    return render_template('chat.html',
                         current_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                         current_user="nicknet06")

@app.route('/admin/dashboard')
def admin_dashboard():
    try:
        reports = EmergencyReport.query.order_by(EmergencyReport.created_at.desc()).all()
        services = EmergencyService.query.filter_by(is_active=True).all()
        return render_template('admin_dashboard.html',
                             reports=reports,
                             services=services,
                             current_time="2025-02-17 01:07:12",
                             current_user="nicknet06")
    except Exception as e:
        flash(f'Error accessing database: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/api/services')
def get_services():
    try:
        with app.app_context():
            print("Attempting to fetch services...")
            services = EmergencyService.query.filter_by(is_active=True).all()
            print(f"Found {len(services)} active services")
            result = []
            for service in services:
                service_dict = {
                    'id': service.id,
                    'name': service.name,
                    'service_type': service.service_type,
                    'city': service.city,
                    'latitude': float(service.latitude),
                    'longitude': float(service.longitude),
                    'address': service.address,
                    'phone': service.phone,
                    'is_active': service.is_active,
                    'created_at': service.created_at.isoformat() if service.created_at else None
                }
                print(f"Converting service: {service_dict['name']}")
                result.append(service_dict)
            print(f"Converted {len(result)} services to JSON")
            return jsonify(result)
    except Exception as e:
        print(f"Error in get_services: {str(e)}")
        logging.error(f"Error fetching services: {str(e)}")
        return jsonify({'error': 'Failed to fetch services', 'details': str(e)}), 500


@app.route('/api/services/<int:service_id>/resources')
def get_service_resources(service_id):
    try:
        equipment = Equipment.query.filter_by(service_id=service_id).all()
        vehicles = Vehicle.query.filter_by(service_id=service_id).all()
        personnel = Personnel.query.filter_by(service_id=service_id).all()

        return jsonify({
            'equipment': [e.to_dict() for e in equipment],
            'vehicles': [v.to_dict() for v in vehicles],
            'personnel': [p.to_dict() for p in personnel],
            'timestamp': "2025-02-17 00:16:55",
            'user': "nicknet06"
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': "2025-02-17 00:16:55",
            'user': "nicknet06"
        }), 500


@app.route('/api/resources/request', methods=['POST'])
def request_resource():
    try:
        data = request.get_json()

        new_request = ResourceRequest(
            service_id=data['service_id'],
            equipment_id=data.get('equipment_id'),
            vehicle_id=data.get('vehicle_id'),
            personnel_id=data.get('personnel_id'),
            requester=data['requester'],
            purpose=data['purpose'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            status='pending'
        )

        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            'message': 'Request submitted successfully',
            'request_id': new_request.id,
            'status': 'pending',
            'timestamp': "2025-02-17 00:16:55",
            'user': "nicknet06"
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': "2025-02-17 00:16:55",
            'user': "nicknet06"
        }), 500


@app.route('/api/debug/db')
def debug_db():
    try:
        with app.app_context():
            # Test basic database connectivity
            db_test = EmergencyService.query.first()
            total_count = EmergencyService.query.count()
            active_count = EmergencyService.query.filter_by(is_active=True).count()

            return jsonify({
                'database_uri': app.config['SQLALCHEMY_DATABASE_URI'],
                'connection_test': 'success' if db_test else 'no data but connected',
                'first_record': db_test.to_dict() if db_test else None,
                'total_records': total_count,
                'active_records': active_count,
                'timestamp': "2025-02-17 00:16:55",
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'database_uri': app.config['SQLALCHEMY_DATABASE_URI'],
            'timestamp': "2025-02-17 00:16:55",
        }), 500


@app.route('/api/statistics')
def get_statistics():
    try:
        with app.app_context():
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

            total_services = EmergencyService.query.count()
            print(f"Total services: {total_services}")

            active_services = EmergencyService.query.filter_by(is_active=True).count()
            print(f"Active services: {active_services}")

            hospitals = EmergencyService.query.filter_by(service_type='hospital', is_active=True).count()
            print(f"Hospitals: {hospitals}")

            police = EmergencyService.query.filter_by(service_type='police', is_active=True).count()
            print(f"Police stations: {police}")

            fire = EmergencyService.query.filter_by(service_type='fire', is_active=True).count()
            print(f"Fire stations: {fire}")

            total_reports = EmergencyReport.query.count()
            print(f"Total reports: {total_reports}")

            recent_reports = EmergencyReport.query.filter(
                EmergencyReport.created_at >= datetime.utcnow().date()
            ).count()
            print(f"Recent reports: {recent_reports}")

            stats = {
                'total_services': total_services,
                'active_services': active_services,
                'hospitals': hospitals,
                'police_stations': police,
                'fire_stations': fire,
                'total_reports': total_reports,
                'recent_reports': recent_reports,
                'database_uri': app.config['SQLALCHEMY_DATABASE_URI']
            }
            return jsonify(stats)
    except Exception as e:
        logging.error(f"Error fetching statistics: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch statistics',
            'details': str(e),
            'database_uri': app.config['SQLALCHEMY_DATABASE_URI']
        }), 500


@app.route('/admin/reports')
def admin_reports():
    try:
        reports = EmergencyReport.query.order_by(EmergencyReport.created_at.desc()).all()
        return render_template('admin_reports.html',
                               reports=reports,
                               current_time="2025-02-17 00:16:55",
                               current_user="nicknet06")
    except Exception as e:
        flash(f'Error accessing database: {str(e)}', 'error')
        return redirect(url_for('home'))


@app.route('/upload-audio', methods=['POST', 'OPTIONS'])
def upload_audio():
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
    else:
        try:
            # Check if an audio file was included in the request
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file'}), 400

            # Get the audio file from the request
            audio_file = request.files['audio']

            # Create a unique filename using current timestamp
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f'emergency_recording_{timestamp}.wav'

            # Create the full filepath
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Ensure the upload directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Save the file
            audio_file.save(filepath)

            # Log the successful upload
            logging.info(f"Audio file saved: {filename}")

            # Return success response
            return jsonify({
                'filename': filename,
                'message': 'Audio uploaded successfully'
            }), 200

        except Exception as e:
            # Log and return any errors that occur
            logging.error(f"Error uploading audio: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Add CORS headers to the response
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response


@app.route('/api/resources/<int:resource_id>/status', methods=['GET'])
def get_resource_status(resource_id):
    try:
        equipment = Equipment.query.get(resource_id)
        if equipment:
            return jsonify({
                'id': equipment.id,
                'name': equipment.name,
                'available': equipment.available,
                'condition': equipment.condition,
                'timestamp': "2025-02-17 00:22:26",
                'user': "nicknet06"
            })
        return jsonify({'error': 'Resource not found'}), 404
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': "2025-02-17 00:22:26",
            'user': "nicknet06"
        }), 500


@app.route('/api/resources/requests/<int:request_id>', methods=['PUT'])
def update_resource_request(request_id):
    try:
        data = request.get_json()
        resource_request = ResourceRequest.query.get(request_id)

        if not resource_request:
            return jsonify({
                'error': 'Request not found',
                'timestamp': "2025-02-17 00:22:26",
                'user': "nicknet06"
            }), 404

        resource_request.status = data['status']
        db.session.commit()

        return jsonify({
            'message': 'Request updated successfully',
            'status': resource_request.status,
            'timestamp': "2025-02-17 00:22:26",
            'user': "nicknet06"
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': "2025-02-17 00:22:26",
            'user': "nicknet06"
        }), 500


@app.route('/api/resources/requests', methods=['GET'])
def list_resource_requests():
    try:
        requests = ResourceRequest.query.all()
        return jsonify({
            'requests': [request.to_dict() for request in requests],
            'timestamp': "2025-02-17 00:22:26",
            'user': "nicknet06"
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': "2025-02-17 00:22:26",
            'user': "nicknet06"
        }), 500


@app.route('/api/services/<int:service_id>/availability', methods=['GET'])
def get_service_availability(service_id):
    try:
        equipment_available = Equipment.query.filter_by(
            service_id=service_id
        ).with_entities(
            db.func.sum(Equipment.available).label('available'),
            db.func.sum(Equipment.quantity).label('total')
        ).first()

        vehicles_available = Vehicle.query.filter_by(
            service_id=service_id,
            status='available'
        ).count()
        total_vehicles = Vehicle.query.filter_by(service_id=service_id).count()

        personnel_available = Personnel.query.filter_by(
            service_id=service_id,
            status='on-duty'
        ).count()
        total_personnel = Personnel.query.filter_by(service_id=service_id).count()

        return jsonify({
            'equipment': {
                'available': equipment_available.available or 0,
                'total': equipment_available.total or 0
            },
            'vehicles': {
                'available': vehicles_available,
                'total': total_vehicles
            },
            'personnel': {
                'available': personnel_available,
                'total': total_personnel
            },
            'timestamp': "2025-02-17 00:22:26",
            'user': "nicknet06"
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': "2025-02-17 00:22:26",
            'user': "nicknet06"
        }), 500


@app.route('/api/resources/maintenance', methods=['POST'])
def schedule_maintenance():
    try:
        data = request.get_json()
        equipment = Equipment.query.get(data['equipment_id'])

        if not equipment:
            return jsonify({
                'error': 'Equipment not found',
                'timestamp': "2025-02-17 00:22:26",
                'user': "nicknet06"
            }), 404

        equipment.condition = 'maintenance'
        equipment.available = max(0, equipment.available - 1)
        equipment.last_maintenance = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Maintenance scheduled successfully',
            'equipment_id': equipment.id,
            'new_condition': equipment.condition,
            'available': equipment.available,
            'timestamp': "2025-02-17 00:22:26",
            'user': "nicknet06"
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': "2025-02-17 00:22:26",
            'user': "nicknet06"
        }), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html',
                           current_time="2025-02-17 00:22:26",
                           current_user="nicknet06"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html',
                           current_time="2025-02-17 00:22:26",
                           current_user="nicknet06"), 500


def init_app():
    """Initialize the Flask application."""
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created successfully")


if __name__ == '__main__':
    print("\nApplication Startup Information:")
    print("--------------------------------")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Base directory: {BASE_DIR}")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Current time (UTC): 2025-02-17 00:22:26")
    print(f"Current user: nicknet06")

    if os.path.exists(app.template_folder):
        print(f"Available templates: {os.listdir(app.template_folder)}")
    else:
        print(f"Warning: Template folder not found at {app.template_folder}")

    print("\nStarting database connection...")
    wait_for_db()
    init_app()

    print("\nStarting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)