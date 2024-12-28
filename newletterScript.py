from flask_mail import Mail, Message
from models import Subscriber
from flask import render_template
from app import db, app  # Import the db and app instances from your main application file
from models import Subscriber


def send_newsletter():
    with app.app_context():
        subscribers = Subscriber.query.all()
        for subscriber in subscribers:
            unsubscribe_link = f"https://127.0.0.1:5002/unsubscribe?email={subscriber.email}"
            msg = Message('Newsletter', sender='levi.rami@gmail.com', recipients=[subscriber.email])
            msg.html = render_template('newsletter.html', unsubscribe_link=unsubscribe_link)  # Your email template
            mail = Mail(app) 
            mail.send(msg)
            print(f"Newsletter sent to {subscriber.email}")



if __name__ == "__main__":
    send_newsletter()