from flask import Flask, jsonify, request
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_instance')))
from database import db
from models import Ride

app = Flask(__name__, instance_relative_config=True)

# Shared database configuration
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_instance', 'ride.db'))

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'offer_service_secret_key'

db.init_app(app)

@app.route('/offer_rides', methods=['POST'])
def offer_rides():
    data = request.form

    required_fields = ["origin", "destination", "date", "time", "seats_available", "price"]
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    ride = Ride(
        origin=data['origin'],
        destination=data['destination'],
        date=datetime.strptime(data['date'], "%Y-%m-%d").date(),
        time=datetime.strptime(data['time'], "%H:%M").time(),
        seats_available=int(data['seats_available']),
        price=float(data.get('price') or 0)
    )


    db.session.add(ride)
    db.session.commit()

    return jsonify({"message": "Ride created", "ride_id": ride.id}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5002, debug=True)
