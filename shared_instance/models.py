# shared_instance/models.py

from database import db

class RideOffer(db.Model):
    __tablename__ = 'ride_offer'   # Critical for table name

    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(255))
    destination = db.Column(db.String(255))
    stop_at = db.Column(db.String(255))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    seats_available = db.Column(db.Integer)
    price = db.Column(db.Float)
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(100))
    car_model = db.Column(db.String(100))
    car_color = db.Column(db.String(100))
    car_plate_number = db.Column(db.String(100))
    origin_lat = db.Column(db.Float)
    origin_lng = db.Column(db.Float)
    destination_lat = db.Column(db.Float)
    destination_lng = db.Column(db.Float)
    stops_latlng = db.Column(db.Text)
