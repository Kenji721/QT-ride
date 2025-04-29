from database import db

class DriverProfile(db.Model):
    __tablename__ = 'driver_profile'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(100))
    car_model = db.Column(db.String(100))
    car_color = db.Column(db.String(100))
    car_plate_number = db.Column(db.String(100))
