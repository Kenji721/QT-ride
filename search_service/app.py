from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_instance')))
from database import db
from models import Ride

app = Flask(__name__, instance_relative_config=True)

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_instance', 'ride.db'))
os.makedirs(os.path.dirname(db_path), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'search_service_secret_key'

db.init_app(app)
#migrate = Migrate(app, db)

#from models import Ride  # Import after initializing db

@app.route('/search_rides', methods=['GET'])
def search_rides():
    rides = Ride.query.all()
    rides_list = [
        {
            "id": ride.id,
            "origin": ride.origin,
            "destination": ride.destination,
            "date": ride.date.strftime("%Y-%m-%d"),
            "time": ride.time.strftime("%H:%M:%S"),
            "seats_available": ride.seats_available,
            "price": ride.price,
            "date_created": ride.date_created.isoformat()
        } for ride in rides
    ]
    return jsonify(rides_list), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1',port=5003, debug=True)