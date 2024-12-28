import sys, os, re
from datetime import datetime
from flask import Flask, request, redirect, flash, render_template, url_for, jsonify
from flask_mail import Mail, Message
from flask_migrate import Migrate
from models import *
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.append(scripts_dir)
from flask import request, redirect, render_template
from database import db, migrate
from flask import Flask, render_template, request, redirect, url_for
from models import User  # Import your User model
from flask_login import LoginManager, current_user, login_user, logout_user
from collections import defaultdict
import stripe

# for future in case payment will be needed.
stripe.api_key = "your_stripe_api_key_here"

# Define a context processor to make current_user available to all templates
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/xvpn/Desktop/QTride/site.db' # add the location of your sqlite db file
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.init_app(app)
db.init_app(app)
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Configure your mail settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'levi.rami@gmail.com'  # 
app.config['MAIL_PASSWORD'] = 'xtqk fcuk zufj rnrh'  # 
app.config['MAIL_DEFAULT_SENDER'] = 'levi.rami@gmail.com'  # Default sender

from flask_login import current_user

# application routes
@app.route('/')
def main():
    title="QT-Ride"
    return render_template('index.html', title=title)  # Ensure you have an index.html template

@app.route('/index')
def index():
    title="QT-ride"
    return render_template('index.html', title=title)  # Ensure you have an index.html template

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    per_page = 3
    # Regular rendering without search results
    blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
 #  print([blog.author for blog in blog_posts])  # Add this line for debugging
    return render_template('blog.html', blog_posts=blog_posts)

#in the meantime redirect to under construction page
@app.route('/offerRide')
def courses():
    return render_template('underconstruction.html')  

#in the meantime redirect to under construction page]
@app.route('/searchRide')
def mentorship():
    return render_template('underconstruction.html')

@app.route('/team')
def team():
    title="QT-ride"
    return render_template('team.html', title=title) 

@app.route('/contactus')
def contactus():
    title="QT-ride"
    return render_template('contactus.html', title=title)

@app.route('/blogs/<int:blog_id>', methods=['GET', 'POST'])
def blog_comments(blog_id):

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
            
        # Add the new comment to the database
        new_comment = Comment(name=name, email=email, message=message, blog_id=blog_id)
        db.session.add(new_comment)
        db.session.commit()
        
    # Fetch comments for the current blog post from the database
    comments = Comment.query.filter_by(blog_id=blog_id).all()
    template_name = f'blogs/{blog_id}.html'
    return render_template(template_name, comments=comments, blog_id=blog_id)


# Initialize Flask-Mail

mail = Mail(app)
@app.route('/send_email', methods=['POST'])
def send_email():
    name = request.form['name']
    email = request.form['email']
    project_type = request.form['project-type']
    message = request.form['msg']

    # Email subject
    subject = f"New contact from {name}"

    # Email body content
    body = f"Name: {name}\nEmail: {email}\nProject Type: {project_type}\n\nMessage:\n{message}"

    # Create message object
    msg = Message(subject, recipients=[app.config['MAIL_DEFAULT_SENDER']], body=body)
    try:
        mail.send(msg)
        flash('Your message has been sent successfully!')
    except Exception as e:
        flash('Something went wrong while sending your message. Please try again.')
        print(e)

    return redirect('/')
 

@app.route('/subscribe', methods=['POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form.get('client-mail')
        if not email:
            flash("Email address is required for subscription.", "error")
            return redirect(url_for('blog'))  # Redirect to the blog page if email is not provided

        # Check if the email is already subscribed
        existing_subscriber = Subscriber.query.filter_by(email=email).first()
        if existing_subscriber:
            flash("You are already subscribed!", "warning")
            return redirect(url_for('blog'))

        # Create a new subscriber instance with the signup date set to the current datetime
        new_subscriber = Subscriber(email=email, signup_date=datetime.utcnow(), active=True)

        # Add the new subscriber to the database
        db.session.add(new_subscriber)
        db.session.commit()

        flash("You have successfully subscribed to the weekly newsletter!", "success")
        return redirect(url_for('blog'))


# Define the search_route_handler function
def search_route_handler():
    query = request.args.get('query')
    if query=='test':
        relevant_posts = [
            {'title': 'Post 1', 'content': 'Content of Post 1'},
            {'title': 'Post 2', 'content': 'Content of Post 2'},
            {'title': 'Post 3', 'content': 'Content of Post 3'}
     ]
        return render_template("blog.html", blog_posts=relevant_posts)

    # Simulate querying database for relevant blog posts
    else: 
         # Handle empty query
        # No search query provided, display all blog posts paginated
        empty_posts = [{}]  # Simulated blog posts data
        return render_template("blog.html", blog_posts=empty_posts)
 
 
@app.route("/search")
def search():
    query = request.args.get("query")
    if not query:
        # Handle empty query
       # No search query provided, display all blog posts paginated
        page = request.args.get('page', 1, type=int)
        per_page = 3
        blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return render_template("blog.html", blog_posts=blog_posts)
    
    # Query database for relevant blog posts
    relevant_posts = (
        db.session.query(BlogPost)
        .filter(BlogPost.keywords.any(Keyword.text.like(f"%{query}%"))).paginate(page=1, per_page=3, error_out=False)

    )
    return render_template("blog.html", blog_posts=relevant_posts)

# Route to handle unsubscribing
@app.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    if request.method == 'POST':
        email = request.form.get('email')
        subscriber = Subscriber.query.filter_by(email=email).first()
        if subscriber:
            db.session.delete(subscriber)
            db.session.commit()
            return render_template('unsubscribe_success.html')
        else:
            return "Email not found."
    elif request.method == 'GET':
        email = request.args.get('email')
        if email:
            subscriber = Subscriber.query.filter_by(email=email).first()
            if subscriber:
                db.session.delete(subscriber)
                db.session.commit()
                return render_template('unsubscribe_success.html')
            else:
                return "Email not found."
        else:
            return render_template('unsubscribe.html')
    else:
        return "Method not allowed", 405

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Check if email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
           message= "You are already signed up!"
           return render_template('sign-in.html' ,message=message) 
        if not is_valid_password(password):
            return 'Invalid password', 400  # Return an error response
              
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # if successful singup render index page as a signed in user.
        message="You signed up successfully"
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Set active status to 1
            user.active = 1
            db.session.commit()
            login_user(user)
            message = "You signed in successfully"
            return render_template('index.html', message=message)


    # Render the signup form template for GET requests
    return render_template('sign-in.html')

def is_valid_password(password):
    # Check if the password is at least 8 characters long
    if len(password) < 8:
        return False

    # Check if the password contains at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        return False

    # Check if the password contains at least one lowercase letter
    if not re.search(r"[a-z]", password):
        return False

    # Check if the password contains at least one digit
    if not re.search(r"\d", password):
        return False

    # Check if the password contains at least one special character
    if not re.search(r"[!@#$%^&*()-_+=]", password):
        return False

    # If all conditions are met, return True
    return True


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Check if user with given email exists
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Set active status to 1
            user.active = 1
            db.session.commit()
            login_user(user)
        # Redirect to the index or any other page after successful sign-in
            message = "You signed in successfully"
            return render_template('index.html', message=message)
        else:
        # Handle invalid credentials
            message="Invalid email or password"
            return render_template('sign-in.html', message=message)
        
    else:
        # Render the sign-in form template for GET requests
        return render_template('sign-in.html')

@app.route('/signout')
# @login_required (might be useful in the future as for now signout is visable to logged in and not loggin users)
def signout():
    if current_user.is_authenticated:
        current_user.active = 0
        db.session.commit()
        logout_user()
        message="Successfully signed out"
        return render_template('index.html', message=message)
    else:
        message="You are not signed in."
        return render_template('index.html', message=message)
    

@login_manager.user_loader
def load_user(user_id):
    # Assuming you have a User model defined with SQLAlchemy
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    ssl_context = ('cert.pem', 'key.pem')
    app.secret_key = 'your_secret_key'  # Needed for flashing messages
    app.run(host='127.0.0.1', port=5002, ssl_context=('cert.pem', 'key_decrypted.pem'), debug=True)

