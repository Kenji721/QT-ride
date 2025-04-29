from flask import Flask, request, jsonify
import sys, os
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_instance')))
from database import db
from models import DriverProfile

app = Flask(__name__, instance_relative_config=True)

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'profile.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'user_profile_secret_key'
app.config['JWT_SECRET'] = 'your_secret'

db.init_app(app)

def decode_token_from_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]  # Get token part
    try:
        decoded = jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
        return decoded
    except (ExpiredSignatureError, InvalidTokenError) as e:
        print("JWT decode error:", e)
        return None


@app.route('/get_profile', methods=['GET'])
def get_profile():
    user = decode_token_from_request()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    email = user['email']
    profile = DriverProfile.query.filter_by(email=email).first()
    if profile:
        return jsonify({
            "driver_name": profile.driver_name,
            "driver_phone": profile.driver_phone,
            "car_model": profile.car_model,
            "car_color": profile.car_color,
            "car_plate_number": profile.car_plate_number
        }), 200
    else:
        return jsonify({}), 200

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user = decode_token_from_request()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    email = user['email']
    data = request.get_json()

    profile = DriverProfile.query.filter_by(email=email).first()
    if not profile:
        profile = DriverProfile(email=email)

    profile.driver_name = data.get('driver_name')
    profile.driver_phone = data.get('driver_phone')
    profile.car_model = data.get('car_model')
    profile.car_color = data.get('car_color')
    profile.car_plate_number = data.get('car_plate_number')

    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "Profile updated successfully"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5005, debug=True)
