import sys, os, re
import jwt
from datetime import datetime
from flask import Flask, request, redirect, flash, render_template, url_for, jsonify, make_response
from flask_mail import Mail, Message
from flask_migrate import Migrate
from models import *
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.append(scripts_dir)
from models import User  # Import your User model
from flask_login import LoginManager, current_user, login_user, logout_user
from collections import defaultdict
import stripe
import requests

stripe.api_key = "your_stripe_api_key_here"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_very_secret_and_secure_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['AUTH_SERVICE_URL'] = "http://127.0.0.1:5001"
app.config['OFFER_SERVICE_URL'] = "http://127.0.0.1:5004"
app.config['SEARCH_SERVICE_URL'] = "http://127.0.0.1:5003"
app.config['USER_PROFILE_SERVICE_URL'] = "http://127.0.0.1:5005"

login_manager = LoginManager(app)
login_manager.init_app(app)

db.init_app(app)
migrate = Migrate(app, db)

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'levi.rami@gmail.com'
app.config['MAIL_PASSWORD'] = 'xtqk fcuk zufj rnrh'
app.config['MAIL_DEFAULT_SENDER'] = 'levi.rami@gmail.com'
mail = Mail(app)

# -- routes --

@app.route('/')
def main():
    return render_template('index.html', title="QT-Ride")

@app.route('/index')
def index():
    return render_template('index.html', title="QT-ride")

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    per_page = 3
    blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('blog.html', blog_posts=blog_posts)

@app.route('/offerRide', methods=['GET','POST'])
def offer_rides():
    if request.method == 'POST':
        # 1) collect ride data only
        ride_data = {
            "origin": request.form['origin'],
            "destination": request.form['destination'],
            "stop_at": request.form.get('stop_at'),
            "date": request.form['date'],
            "time": request.form['time'],
            "seats_available": request.form['seats_available'],
            "price": request.form.get('price') or 0,
            # placeholder for driver fields
            "driver_name": None,
            "driver_phone": None,
            "car_model": None,
            "car_color": None,
            "car_plate_number": None,
            "origin_lat": request.form.get('origin_lat'),
            "origin_lng": request.form.get('origin_lng'),
            "destination_lat": request.form.get('destination_lat'),
            "destination_lng": request.form.get('destination_lng'),
            "stops_latlng": request.form.get('stops_latlng')
        }

        # 2) fetch the current user's profile from your profile microservice
        token = request.cookies.get('access_token')
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        try:
            resp = requests.get(
                f"{app.config['USER_PROFILE_SERVICE_URL']}/get_profile",
                headers=headers
            )
            resp.raise_for_status()
            profile = resp.json()
            # 3) merge in the driver/car fields
            ride_data.update({
                "driver_name": profile.get("driver_name"),
                "driver_phone": profile.get("driver_phone"),
                "car_model": profile.get("car_model"),
                "car_color": profile.get("car_color"),
                "car_plate_number": profile.get("car_plate_number")
            })
        except Exception as e:
            app.logger.error(f"Could not fetch profile to attach to ride: {e}")
            flash("Unable to load your driver profile – ride not offered.", "danger")
            return redirect(url_for('offer_rides'))

        # 4) forward to offer‐service
        try:
            offer_resp = requests.post(
                f"{app.config['OFFER_SERVICE_URL']}/offer_rides",
                data=ride_data
            )
            if offer_resp.status_code == 201:
                flash('Ride created successfully!', 'success')
            else:
                flash('Could not offer ride. Please try again.', 'danger')
        except Exception as e:
            app.logger.error(f'Error contacting offer service: {e}')
            flash('Could not offer ride. Please try again later.', 'danger')

        return redirect(url_for('offer_rides'))
    return render_template('offer_ride.html')

@app.route('/searchRide')
def search_rides():
    try:
        resp = requests.get(f"{app.config['SEARCH_SERVICE_URL']}/search_rides")
        resp.raise_for_status()
        rides = resp.json()
    except Exception as e:
        app.logger.error(f'Error contacting search service: {e}')
        rides = []
    return render_template('search_ride.html', rides=rides,  today=datetime.utcnow().strftime("%Y-%m-%d"),
                           now=datetime.utcnow().strftime("%H:%M"))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('signin'))

    # pull JWT from browser cookie and build Authorization header
    token = request.cookies.get('access_token')
    if not token:
        flash("No session token; please sign in again.", "danger")
        return redirect(url_for('signin'))
    headers = {'Authorization': f'Bearer {token}'}

    if request.method == 'POST':
        data = {
            "driver_name": request.form.get('driver_name'),
            "driver_phone": request.form.get('driver_phone'),
            "car_model": request.form.get('car_model'),
            "car_color": request.form.get('car_color'),
            "car_plate_number": request.form.get('car_plate_number')
        }
        try:
            resp = requests.post(f"{app.config['USER_PROFILE_SERVICE_URL']}/update_profile",
                                 json=data, headers=headers)
            resp.raise_for_status()
            flash("Profile updated successfully", "success")
        except Exception as e:
            flash("Error updating profile", "danger")
            app.logger.error(f"Profile update error: {e}")

    driver_profile = {}
    try:
        resp = requests.get(f"{app.config['USER_PROFILE_SERVICE_URL']}/get_profile", headers=headers)
        resp.raise_for_status()
        driver_profile = resp.json()
    except Exception as e:
        flash("Error fetching profile information", "danger")
        app.logger.error(f"Profile retrieval error: {e}")

    return render_template('profile.html', driver_profile=driver_profile)

@app.route('/team')
def team():
    return render_template('team.html', title="QT-ride")

@app.route('/contactus')
def contactus():
    return render_template('contactus.html', title="QT-ride")

@app.route('/blogs/<int:blog_id>', methods=['GET', 'POST'])
def blog_comments(blog_id):
    if request.method == 'POST':
        new_comment = Comment(
            name=request.form['name'],
            email=request.form['email'],
            message=request.form['message'],
            blog_id=blog_id
        )
        db.session.add(new_comment)
        db.session.commit()
    comments = Comment.query.filter_by(blog_id=blog_id).all()
    return render_template(f'blogs/{blog_id}.html', comments=comments, blog_id=blog_id)

@app.route('/send_email', methods=['POST'])
def send_email():
    msg = Message(
        f"New contact from {request.form['name']}",
        recipients=[app.config['MAIL_DEFAULT_SENDER']],
        body=(f"Name: {request.form['name']}\n"
              f"Email: {request.form['email']}\n"
              f"Project Type: {request.form['project-type']}\n\n"
              f"Message:\n{request.form['msg']}")
    )
    try:
        mail.send(msg)
        flash('Your message has been sent successfully!')
    except Exception as e:
        flash('Something went wrong while sending your message. Please try again.')
        app.logger.error(e)
    return redirect('/')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('client-mail')
    if not email:
        flash("Email address is required for subscription.", "error")
        return redirect(url_for('blog'))
    if Subscriber.query.filter_by(email=email).first():
        flash("You are already subscribed!", "warning")
        return redirect(url_for('blog'))
    new_sub = Subscriber(email=email, signup_date=datetime.utcnow(), active=True)
    db.session.add(new_sub)
    db.session.commit()
    flash("You have successfully subscribed to the weekly newsletter!", "success")
    return redirect(url_for('blog'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = {"email": request.form['email'], "password": request.form['password']}
        try:
            resp = requests.post(f"{app.config['AUTH_SERVICE_URL']}/signup", json=data, verify=False)
            if resp.status_code == 201:
                user = User(email=data['email'], signup_date=datetime.utcnow(), active=True)
                db.session.add(user)
                db.session.commit()
                flash("Signup successful! Please log in.", "success")
                return redirect(url_for('signin'))
            else:
                flash(resp.json().get("message", "Signup failed"), "danger")
        except Exception as e:
            flash("An error occurred. Please try again.", "danger")
            app.logger.error(e)
    return render_template('sign-in.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        data = {"email": request.form['email'], "password": request.form['password']}
        try:
            resp = requests.post(f"{app.config['AUTH_SERVICE_URL']}/signin", json=data, verify=False)
            if resp.status_code == 200:
                token = resp.cookies.get('access_token')
                if not token:
                    flash("Authentication token missing.", "danger")
                    return redirect(url_for('signin'))
                user = User.query.filter_by(email=data['email']).first()
                if not user:
                    user = User(email=data['email'], signup_date=datetime.utcnow(), active=True)
                    db.session.add(user)
                    db.session.commit()
                user.active = True
                db.session.commit()
                login_user(user)
                flask_resp = make_response(redirect(url_for('index')))
                flask_resp.set_cookie('access_token', token, httponly=True)
                flash("Signin successful!", "success")
                return flask_resp
            else:
                flash("Invalid email or password.", "danger")
        except Exception as e:
            flash("An error occurred. Please try again.", "danger")
            app.logger.error(e)
    return render_template('sign-in.html')

@app.route('/signout')
def signout():
    resp = requests.post(f"{app.config['AUTH_SERVICE_URL']}/signout", verify=False)
    if resp.status_code == 200 and current_user.is_authenticated:
        current_user.active = False
        db.session.commit()
        logout_user()
        flash('Successfully signed out!', 'success')
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5002, debug=True)
