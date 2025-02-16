from app import app
from models import db, EmergencyService
from datetime import datetime
from sqlalchemy import inspect
# Empty array for emergency services in Greece - to be populated
services = [
  {
    "name": "Athens General Hospital",
    "service_type": "hospital",
    "city": "Athens",
    "latitude": 35.0,
    "longitude": 24.0,
    "address": "Athens General Hospital Address",
    "phone": "+30 210100000"
  },
  {
    "name": "Athens Police Department",
    "service_type": "police",
    "city": "Athens",
    "latitude": 35.005,
    "longitude": 24.005,
    "address": "Athens Police Department Address",
    "phone": "+30 210200000"
  },
  {
    "name": "Athens Fire Department 1",
    "service_type": "fire",
    "city": "Athens",
    "latitude": 35.01,
    "longitude": 24.01,
    "address": "Athens Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Athens Fire Department 2",
    "service_type": "fire",
    "city": "Athens",
    "latitude": 35.015,
    "longitude": 24.015,
    "address": "Athens Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Thessaloniki General Hospital",
    "service_type": "hospital",
    "city": "Thessaloniki",
    "latitude": 35.1,
    "longitude": 24.1,
    "address": "Thessaloniki General Hospital Address",
    "phone": "+30 210100001"
  },
  {
    "name": "Thessaloniki Police Department",
    "service_type": "police",
    "city": "Thessaloniki",
    "latitude": 35.105,
    "longitude": 24.105,
    "address": "Thessaloniki Police Department Address",
    "phone": "+30 210200001"
  },
  {
    "name": "Thessaloniki Fire Department 1",
    "service_type": "fire",
    "city": "Thessaloniki",
    "latitude": 35.11,
    "longitude": 24.11,
    "address": "Thessaloniki Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Thessaloniki Fire Department 2",
    "service_type": "fire",
    "city": "Thessaloniki",
    "latitude": 35.115,
    "longitude": 24.115,
    "address": "Thessaloniki Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Patras General Hospital",
    "service_type": "hospital",
    "city": "Patras",
    "latitude": 35.2,
    "longitude": 24.2,
    "address": "Patras General Hospital Address",
    "phone": "+30 210100002"
  },
  {
    "name": "Patras Police Department",
    "service_type": "police",
    "city": "Patras",
    "latitude": 35.205,
    "longitude": 24.205,
    "address": "Patras Police Department Address",
    "phone": "+30 210200002"
  },
  {
    "name": "Patras Fire Department 1",
    "service_type": "fire",
    "city": "Patras",
    "latitude": 35.21,
    "longitude": 24.21,
    "address": "Patras Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Patras Fire Department 2",
    "service_type": "fire",
    "city": "Patras",
    "latitude": 35.215,
    "longitude": 24.215,
    "address": "Patras Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Heraklion General Hospital",
    "service_type": "hospital",
    "city": "Heraklion",
    "latitude": 35.3,
    "longitude": 24.3,
    "address": "Heraklion General Hospital Address",
    "phone": "+30 210100003"
  },
  {
    "name": "Heraklion Police Department",
    "service_type": "police",
    "city": "Heraklion",
    "latitude": 35.305,
    "longitude": 24.305,
    "address": "Heraklion Police Department Address",
    "phone": "+30 210200003"
  },
  {
    "name": "Heraklion Fire Department 1",
    "service_type": "fire",
    "city": "Heraklion",
    "latitude": 35.31,
    "longitude": 24.31,
    "address": "Heraklion Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Heraklion Fire Department 2",
    "service_type": "fire",
    "city": "Heraklion",
    "latitude": 35.315,
    "longitude": 24.315,
    "address": "Heraklion Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Larissa General Hospital",
    "service_type": "hospital",
    "city": "Larissa",
    "latitude": 35.4,
    "longitude": 24.4,
    "address": "Larissa General Hospital Address",
    "phone": "+30 210100004"
  },
  {
    "name": "Larissa Police Department",
    "service_type": "police",
    "city": "Larissa",
    "latitude": 35.405,
    "longitude": 24.405,
    "address": "Larissa Police Department Address",
    "phone": "+30 210200004"
  },
  {
    "name": "Larissa Fire Department 1",
    "service_type": "fire",
    "city": "Larissa",
    "latitude": 35.41,
    "longitude": 24.41,
    "address": "Larissa Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Larissa Fire Department 2",
    "service_type": "fire",
    "city": "Larissa",
    "latitude": 35.415,
    "longitude": 24.415,
    "address": "Larissa Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Volos General Hospital",
    "service_type": "hospital",
    "city": "Volos",
    "latitude": 35.5,
    "longitude": 24.5,
    "address": "Volos General Hospital Address",
    "phone": "+30 210100005"
  },
  {
    "name": "Volos Police Department",
    "service_type": "police",
    "city": "Volos",
    "latitude": 35.505,
    "longitude": 24.505,
    "address": "Volos Police Department Address",
    "phone": "+30 210200005"
  },
  {
    "name": "Volos Fire Department 1",
    "service_type": "fire",
    "city": "Volos",
    "latitude": 35.51,
    "longitude": 24.51,
    "address": "Volos Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Volos Fire Department 2",
    "service_type": "fire",
    "city": "Volos",
    "latitude": 35.515,
    "longitude": 24.515,
    "address": "Volos Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Ioannina General Hospital",
    "service_type": "hospital",
    "city": "Ioannina",
    "latitude": 35.6,
    "longitude": 24.6,
    "address": "Ioannina General Hospital Address",
    "phone": "+30 210100006"
  },
  {
    "name": "Ioannina Police Department",
    "service_type": "police",
    "city": "Ioannina",
    "latitude": 35.605,
    "longitude": 24.605,
    "address": "Ioannina Police Department Address",
    "phone": "+30 210200006"
  },
  {
    "name": "Ioannina Fire Department 1",
    "service_type": "fire",
    "city": "Ioannina",
    "latitude": 35.61,
    "longitude": 24.61,
    "address": "Ioannina Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Ioannina Fire Department 2",
    "service_type": "fire",
    "city": "Ioannina",
    "latitude": 35.615,
    "longitude": 24.615,
    "address": "Ioannina Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Kavala General Hospital",
    "service_type": "hospital",
    "city": "Kavala",
    "latitude": 35.7,
    "longitude": 24.7,
    "address": "Kavala General Hospital Address",
    "phone": "+30 210100007"
  },
  {
    "name": "Kavala Police Department",
    "service_type": "police",
    "city": "Kavala",
    "latitude": 35.705,
    "longitude": 24.705,
    "address": "Kavala Police Department Address",
    "phone": "+30 210200007"
  },
  {
    "name": "Kavala Fire Department 1",
    "service_type": "fire",
    "city": "Kavala",
    "latitude": 35.71,
    "longitude": 24.71,
    "address": "Kavala Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Kavala Fire Department 2",
    "service_type": "fire",
    "city": "Kavala",
    "latitude": 35.715,
    "longitude": 24.715,
    "address": "Kavala Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Chania General Hospital",
    "service_type": "hospital",
    "city": "Chania",
    "latitude": 35.8,
    "longitude": 24.8,
    "address": "Chania General Hospital Address",
    "phone": "+30 210100008"
  },
  {
    "name": "Chania Police Department",
    "service_type": "police",
    "city": "Chania",
    "latitude": 35.805,
    "longitude": 24.805,
    "address": "Chania Police Department Address",
    "phone": "+30 210200008"
  },
  {
    "name": "Chania Fire Department 1",
    "service_type": "fire",
    "city": "Chania",
    "latitude": 35.81,
    "longitude": 24.81,
    "address": "Chania Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Chania Fire Department 2",
    "service_type": "fire",
    "city": "Chania",
    "latitude": 35.815,
    "longitude": 24.815,
    "address": "Chania Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Kalamata General Hospital",
    "service_type": "hospital",
    "city": "Kalamata",
    "latitude": 35.9,
    "longitude": 24.9,
    "address": "Kalamata General Hospital Address",
    "phone": "+30 210100009"
  },
  {
    "name": "Kalamata Police Department",
    "service_type": "police",
    "city": "Kalamata",
    "latitude": 35.905,
    "longitude": 24.905,
    "address": "Kalamata Police Department Address",
    "phone": "+30 210200009"
  },
  {
    "name": "Kalamata Fire Department 1",
    "service_type": "fire",
    "city": "Kalamata",
    "latitude": 35.91,
    "longitude": 24.91,
    "address": "Kalamata Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Kalamata Fire Department 2",
    "service_type": "fire",
    "city": "Kalamata",
    "latitude": 35.915,
    "longitude": 24.915,
    "address": "Kalamata Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Alexandroupoli General Hospital",
    "service_type": "hospital",
    "city": "Alexandroupoli",
    "latitude": 36.0,
    "longitude": 25.0,
    "address": "Alexandroupoli General Hospital Address",
    "phone": "+30 210100010"
  },
  {
    "name": "Alexandroupoli Police Department",
    "service_type": "police",
    "city": "Alexandroupoli",
    "latitude": 36.005,
    "longitude": 25.005,
    "address": "Alexandroupoli Police Department Address",
    "phone": "+30 210200010"
  },
  {
    "name": "Alexandroupoli Fire Department 1",
    "service_type": "fire",
    "city": "Alexandroupoli",
    "latitude": 36.01,
    "longitude": 25.01,
    "address": "Alexandroupoli Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Alexandroupoli Fire Department 2",
    "service_type": "fire",
    "city": "Alexandroupoli",
    "latitude": 36.015,
    "longitude": 25.015,
    "address": "Alexandroupoli Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Katerini General Hospital",
    "service_type": "hospital",
    "city": "Katerini",
    "latitude": 36.1,
    "longitude": 25.1,
    "address": "Katerini General Hospital Address",
    "phone": "+30 210100011"
  },
  {
    "name": "Katerini Police Department",
    "service_type": "police",
    "city": "Katerini",
    "latitude": 36.105,
    "longitude": 25.105,
    "address": "Katerini Police Department Address",
    "phone": "+30 210200011"
  },
  {
    "name": "Katerini Fire Department 1",
    "service_type": "fire",
    "city": "Katerini",
    "latitude": 36.11,
    "longitude": 25.11,
    "address": "Katerini Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Katerini Fire Department 2",
    "service_type": "fire",
    "city": "Katerini",
    "latitude": 36.115,
    "longitude": 25.115,
    "address": "Katerini Fire Department Address 2",
    "phone": "199"
  },
  {
    "name": "Serres General Hospital",
    "service_type": "hospital",
    "city": "Serres",
    "latitude": 36.2,
    "longitude": 25.2,
    "address": "Serres General Hospital Address",
    "phone": "+30 210100012"
  },
  {
    "name": "Serres Police Department",
    "service_type": "police",
    "city": "Serres",
    "latitude": 36.205,
    "longitude": 25.205,
    "address": "Serres Police Department Address",
    "phone": "+30 210200012"
  },
  {
    "name": "Serres Fire Department 1",
    "service_type": "fire",
    "city": "Serres",
    "latitude": 36.21,
    "longitude": 25.21,
    "address": "Serres Fire Department Address 1",
    "phone": "199"
  },
  {
    "name": "Serres Fire Department 2",
    "service_type": "fire",
    "city": "Serres",
    "latitude": 36.215,
    "longitude": 25.215,
    "address": "Serres Fire Department Address 2",
    "phone": "199"
  }
]


def init_services():
  try:
    with app.app_context():
      # Create both tables
      db.create_all()
      print("Created/Updated database tables")

      # Clear and re-add emergency services
      EmergencyService.query.delete()

      for service_data in services:
        service = EmergencyService(**service_data)
        db.session.add(service)

      db.session.commit()
      print("\nEmergency Services Initialization Report")
      print("---------------------------------------")
      print(f"Successfully initialized {len(services)} emergency services!")
      print(f"Added {len([s for s in services if s['service_type'] == 'hospital'])} hospitals")
      print(f"Added {len([s for s in services if s['service_type'] == 'police'])} police stations")
      print(f"Added {len([s for s in services if s['service_type'] == 'fire'])} fire stations")
      print(f"Current Date and Time (UTC): 2025-02-16 16:46:29")
      print(f"Current User's Login: nicknet06")
      print("---------------------------------------")

  except Exception as e:
    db.session.rollback()
    print(f"Error initializing services: {e}")
    raise e


if __name__ == '__main__':
  print("\nStarting Emergency Services Initialization...")
  print(f"Current Date and Time (UTC): 2025-02-16 16:46:29")
  print(f"Current User's Login: nicknet06")

  with app.app_context():
    init_services()