from models import *
from app import app

with app.app_context():
    # First ensure tables exist
    db.session.remove()
    db.create_all()
    db.session.commit()
    print("Database tables verified\n")

    # Get all emergency services
    print("Emergency Services:")
    print("-" * 50)
    services = db.session.query(Personnel).all()
    for service in services:
        print(service.name)
#     if services:
#         for service in services:
#             print(f"""
# Service ID: {service.id}
# Name: {service.name}
# Type: {service.service_type}
# City: {service.city}
# Address: {service.address}
# Phone: {service.phone}
# Coordinates: ({service.latitude}, {service.longitude})
# Active: {service.is_active}
# Created: {service.created_at}
# {"=" * 50}""")
#     else:
#         print("No emergency services found in database.")
#
#     # Get all emergency reports
#     print("\nEmergency Reports:")
#     print("-" * 50)
#     reports = EmergencyReport.query.all()
#     if reports:
#         for report in reports:
#             print(f"""
# Report ID: {report.id}
# Name: {report.name}
# Contact: {report.contact}
# Location: ({report.latitude}, {report.longitude})
# Description: {report.description}
# Audio File: {report.audio_filename}
# Created: {report.created_at}
# {"=" * 50}""")
#     else:
#         print("No emergency reports found in database.")
#
#     # Print summary
#     print("\nDatabase Summary:")
#     print("-" * 50)
#     print(f"Total Emergency Services: {EmergencyService.query.count()}")
#     print(f"Active Emergency Services: {EmergencyService.query.filter_by(is_active=True).count()}")
#     print(f"Total Emergency Reports: {EmergencyReport.query.count()}")