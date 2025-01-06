from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from database import db
from models import User
#from models import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth_service.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'auth_service_secret_key'


db.init_app(app)
#db = SQLAlchemy(app)
migrate = Migrate(app, db)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=False)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 409

    user = User(email=data['email'])
    user.set_password(data['password'])  # Ensure the password hash is set
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    app.logger.info(f"Received sign-in request for email: {data['email']}")
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        app.logger.info("Sign-in successful")
        return jsonify({'message': 'Signed in successfully'}), 200
    app.logger.info("Sign-in failed: Invalid email or password")
    return jsonify({'message': 'Invalid email or password'}), 401


@app.route('/signout', methods=['POST'])
def signout():
    return jsonify({'message': 'Signed out successfully'}), 200

if __name__ == '__main__':
    with app.app_context():  # Ensure the app context is active
        db.create_all()  # Ensure the database schema is created
    # app.run(host='127.0.0.1', port=5001, ssl_context=('new_cert.pem', 'new_key_decrypted.pem'), debug=True)
    app.run(host='127.0.0.1', port=5001, debug=True)
