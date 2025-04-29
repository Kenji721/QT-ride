from flask import Flask, jsonify, request
from datetime import datetime
import os
import sys
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# Shared database access
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_instance')))
from database import db
from models import RideOffer  # <<< Fix here!

from flask_migrate import Migrate

app = Flask(__name__, instance_relative_config=True)

# Shared DB config
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_instance', 'ride.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'offer_service_secret_key'

# Init DB and migration
db.init_app(app)
migrate = Migrate(app, db)

def decode_token_from_cookie():
    token = request.cookies.get('access_token')
    if not token:
        return None
    try:
        decoded = jwt.decode(token, "your_secret", algorithms=["HS256"])
        return decoded
    except (ExpiredSignatureError, InvalidTokenError):
        return None

from flask import redirect, url_for

from flask import render_template

@app.route('/offer_rides', methods=['GET', 'POST'])
def offer_rides():
    if request.method == 'POST':

        data = request.form

        required_fields = ["origin", "destination", "date", "time", "seats_available", "price",
                           "driver_name", "driver_phone", "car_model", "car_color", "car_plate_number"]
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        ride = RideOffer(
            origin=data['origin'],
            destination=data['destination'],
            date=datetime.strptime(data['date'], "%Y-%m-%d").date(),
            time=datetime.strptime(data['time'], "%H:%M").time(),
            seats_available=int(data['seats_available']),
            price=float(data.get('price') or 0),
            driver_name=data['driver_name'],
            driver_phone=data['driver_phone'],
            car_model=data['car_model'],
            car_color=data['car_color'],
            car_plate_number=data['car_plate_number'],
            stop_at=data.get('stop_at'),
            origin_lat=data.get('origin_lat'),
            origin_lng=data.get('origin_lng'),
            destination_lat=data.get('destination_lat'),
            destination_lng=data.get('destination_lng'),
            stops_latlng=data.get('stops_latlng'),
        )

        db.session.add(ride)
        db.session.commit()

        return jsonify({"message": "Ride created successfully"}), 201

    else:
        # If user does a GET request (wrong way), just show the offerRide page again
        return render_template('offer_ride.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This creates the schema from models
    app.run(host='127.0.0.1', port=5004, debug=True)
