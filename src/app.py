from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_cors import CORS
import logging
import os
import time
from datetime import datetime
from sqlalchemy.exc import OperationalError
from models import *

# Import db and models from models.py
from models import db, EmergencyService, EmergencyReport

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

# Database configuration - Use existing SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, '..', 'db.sqlite3')
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
                print(f"Current time (UTC): 2025-02-16 19:28:58")
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
                           current_time="2025-02-16 19:28:58",
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
            except Exception as db_error:
                db.session.rollback()
                logging.error(f"Database error: {str(db_error)}")
                raise

            location = f"coordinates: {latitude}, {longitude}" if latitude and longitude else "location pending"

            log_message = f"""
            Emergency Report:
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

        except Exception as e:
            logging.error(f"Error processing emergency report: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Failed to process emergency report'}), 500
            else:
                flash('Error processing emergency report. Please try again.', 'error')
                return redirect(url_for('chat'))

    return render_template('chat.html',
                           current_time="2025-02-16 19:28:58",
                           current_user="nicknet06")


@app.route('/admin/dashboard')
def admin_dashboard():
    try:
        reports = EmergencyReport.query.order_by(EmergencyReport.created_at.desc()).all()
        services = EmergencyService.query.filter_by(is_active=True).all()
        return render_template('admin_dashboard.html',
                               reports=reports,
                               services=services,
                               current_time="2025-02-16 19:28:58",
                               current_user="nicknet06")
    except Exception as e:
        flash(f'Error accessing database: {str(e)}', 'error')
        return redirect(url_for('home'))


@app.route('/api/services')
def get_services():
    try:
        print("Attempting to fetch services...")  # Debug log
        services = EmergencyService.query.filter_by(is_active=True).all()
        print(f"Found {len(services)} active services")  # Debug log
        result = []
        for service in services:
            service_dict = service.to_dict()
            print(f"Converting service: {service_dict['name']}")  # Debug log
            result.append(service_dict)
        print(f"Converted {len(result)} services to JSON")  # Debug log
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_services: {str(e)}")  # Debug log
        logging.error(f"Error fetching services: {str(e)}")
        return jsonify({'error': 'Failed to fetch services', 'details': str(e)}), 500


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
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'database_uri': app.config['SQLALCHEMY_DATABASE_URI'],
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        }), 500


@app.route('/admin/reports')
def admin_reports():
    try:
        reports = EmergencyReport.query.order_by(EmergencyReport.created_at.desc()).all()
        return render_template('admin_reports.html',
                               reports=reports,
                               current_time="2025-02-16 19:28:58",
                               current_user="nicknet06")
    except Exception as e:
        flash(f'Error accessing database: {str(e)}', 'error')
        return redirect(url_for('home'))


@app.route('/upload-audio', methods=['POST', 'OPTIONS'])
def upload_audio():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
    else:
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file'}), 400

            audio_file = request.files['audio']
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f'emergency_recording_{timestamp}.wav'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            audio_file.save(filepath)

            return jsonify({
                'filename': filename,
                'message': 'Audio uploaded successfully'
            }), 200
        except Exception as e:
            logging.error(f"Error uploading audio: {str(e)}")
            return jsonify({'error': str(e)}), 500

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response


@app.route('/api/statistics')
def get_statistics():
    try:
        stats = {
            'total_services': EmergencyService.query.count(),
            'active_services': EmergencyService.query.filter_by(is_active=True).count(),
            'hospitals': EmergencyService.query.filter_by(service_type='hospital', is_active=True).count(),
            'police_stations': EmergencyService.query.filter_by(service_type='police', is_active=True).count(),
            'fire_stations': EmergencyService.query.filter_by(service_type='fire', is_active=True).count(),
            'total_reports': EmergencyReport.query.count(),
            'recent_reports': EmergencyReport.query.filter(
                EmergencyReport.created_at >= datetime.utcnow().date()
            ).count()
        }
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Error fetching statistics: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics', 'details': str(e)}), 500


@app.cli.command("list-reports")
def list_reports():
    """List all emergency reports in the database."""
    try:
        with app.app_context():
            reports = EmergencyReport.query.all()
            if not reports:
                print("No reports found in database.")
                return

            for report in reports:
                print(f"""
                ==========================================
                Report ID: {report.id}
                Timestamp: {report.created_at}
                Name: {report.name}
                Contact: {report.contact}
                Location: ({report.latitude}, {report.longitude})
                Description: {report.description}
                Audio File: {report.audio_filename}
                ==========================================
                """)
    except Exception as e:
        print(f"Error: {e}")


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html',
                           current_time="2025-02-16 19:28:58",
                           current_user="nicknet06"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html',
                           current_time="2025-02-16 19:28:58",
                           current_user="nicknet06"), 500


if __name__ == '__main__':
    print("\nApplication Startup Information:")
    print("--------------------------------")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Base directory: {BASE_DIR}")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Current time (UTC): 2025-02-16 19:28:58")
    print(f"Current user: nicknet06")

    if os.path.exists(app.template_folder):
        print(f"Available templates: {os.listdir(app.template_folder)}")
    else:
        print(f"Warning: Template folder not found at {app.template_folder}")

    print("\nStarting database connection...")
    wait_for_db()

    print("\nStarting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)