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
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from collections import defaultdict
import stripe

stripe.api_key = "your_stripe_api_key_here"

# Define a context processor to make current_user available to all templates
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users//site.db' # add the location of your sqlite db file
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
app.config['MAIL_USERNAME'] = 'xyz@xxx.com'  # 
app.config['MAIL_PASSWORD'] = ''  # 
app.config['MAIL_DEFAULT_SENDER'] = 'xxx.yyy@zzz.com'  # Default sender


# application routes

@app.route('/admin/shop', methods=['GET', 'POST'])
def add_product():
    products = Product.query.all()
    if request.method == 'POST':
        # Get form data from the request
        data = request.json
        if data['action'] == 'add_product':
            name = data['name']
            price = float(data['price'])
            description = data['description']   
            image_url = data['description']
            quantity = int(data['quantity'])
        
        # Create a new Product object
            new_product = Product(
                name=name,
                price=price,
                description=description,
                image_url=image_url,
                quantity=quantity
        )

            # Add the new product to the database
            db.session.add(new_product)
            db.session.commit()
        
        # Redirect to the admin shop page
       
            return jsonify({'message': 'Product added successfully'}), 200

    # Render the admin shop page with the form
    return render_template('admin-shop.html', products=products)

@app.route('/update_inventory', methods=['POST'])
def update_inventory_route():
    data = request.json
    product_id = data.get('product_id')
    action = data.get('action')
    if (action== 'add' or action== 'remove' or action== 'delete'):
        update_inventory(product_id, action)
        return jsonify({'message': 'inventory updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400
    
def update_inventory(product_id, action):
    # Logic to update quantity in the database based on the action (add or remove)
    product = Product.query.get(product_id)
    if product:
        # Update the product quantity based on the action
        if action == 'add':
            product.quantity += 1
        elif action == 'remove' and product.quantity > 0:
            product.quantity -= 1
        elif action == 'delete':
            # If there are more than one items, decrement the quantity
            db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Inventory updated successfully'}), 200
    else:
        # Return an error response if the product does not exist
        return jsonify({'error': 'Product not found'}), 404


@app.route('/')
def main():
    title="QED"
    return render_template('index.html', title=title)  # Ensure you have an index.html template

@app.route('/index')
def index():
    title="QED"
    return render_template('index.html', title=title)  # Ensure you have an index.html template

@app.route('/shop')
def shop():
    title="shop"
    products = Product.query.all()  # Retrieve all products from the database
    return render_template('shop.html', products=products)

from flask_login import current_user

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('product_id')
    price = data.get('price')

    if product_id and price:
        # Check if the user is authenticated
        if current_user.is_authenticated:
            user_id = current_user.id

            # Check if the product is already in the cart for the user
            cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
            # Retrieve the product from the database
            product = Product.query.get(product_id)
            
            if cart_item:
                # If the product is already in the cart, update the quantity
                cart_item.quantity += 1
                
            else:
                # If the product is not in the cart, add it
                cart_item = CartItem(user_id=user_id, product_id=product_id, price=price)

            # Reduce the quantity of the product in the Product table
            product = Product.query.get(product_id)
            if product:
                if product.quantity > 0:
                    product.quantity -= 1
                else:
                    if product.quantity == 0:
                        return jsonify({'error': 'out of stock'}), 400
            else:
                return jsonify({'error': 'Product not in stock'}), 404
          
            try:
                db.session.add(cart_item)
                db.session.commit()
                return jsonify({'message': 'Product added to cart successfully'}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': 'Error adding product to cart'}), 500
        else:
            return jsonify({'error': 'User not authenticated'}), 401
    else:
        return jsonify({'error': 'Invalid request'}), 400

def get_product_info(product_id):
    # Replace this with your logic to retrieve product info based on product_id
    # For demonstration, let's assume product_info is a dictionary with product details
    product_info = {
        'name': 'Product Name',
        'description': 'Product Description',
        'price': 10.99,
        'quantity': 5  # Example quantity
    }
    return product_info

@app.route('/mycart')
def mycart():
    # Retrieve cart items from the database (replace this with your own logic)
    user_id = current_user.id
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    # Create a defaultdict to store aggregated quantities and totals for each product
    product_totals = defaultdict(lambda: {'quantity': 0, 'total': 0})
    # Calculate total cost for all items
    total_cost = 0
    product_id = request.args.get('product_id')
     # Retrieve product information based on product ID
    product_info = get_product_info(product_id)
    # Aggregate quantities and totals for each product
    for item in cart_items:
        product_id = item.product_id
        product = Product.query.filter_by(id=product_id).first()  # Fetch product information
        product_name = product.name if product else 'Unknown' 
        product_description = product.description if product else 'Unknown'
        
        product_totals[product_id]['name'] = product_name
        product_totals[product_id]['description'] = product_description
        product_totals[item.product_id]['quantity'] += item.quantity
        product_totals[item.product_id]['total'] += item.price * item.quantity
        # Calculate total cost for all items
        total_cost += item.price * item.quantity

    return render_template('mycart.html', product_totals=product_totals, total_cost=total_cost, product_info=product_info)


def update_quantity(product_id, action):
    # Logic to update quantity in the database based on the action (add or remove)
    cart_item = CartItem.query.filter_by(product_id=product_id).first()
    product = Product.query.get(product_id)

    if cart_item and product:
        if action == 'add':
            if product.quantity > 0:
                cart_item.quantity += 1
                product.quantity -= 1
            
        elif action == 'remove':
            if cart_item.quantity == 1:
                # If there is only one item left, remove the cart item from the database
                db.session.delete(cart_item)
                product.quantity += 1
            else:
                # If there are more than one items, decrement the quantity
                cart_item.quantity -= 1
                product.quantity = max(product.quantity + 1, 0)  # Ensure product quantity doesn't go below 0

        db.session.commit()

@app.route('/update_quantity', methods=['POST'])
def update_quantity_route():
    data = request.json
    product_id = data.get('product_id')
    action = data.get('action')
    product = Product.query.get(product_id)
    if product_id and action:
        # Call the update_quantity function with the provided product_id and action
        if product.quantity == 0 and action =='add':
                return jsonify({'error': 'out of stock'}), 400
        else:
            update_quantity(product_id, action)
            return jsonify({'message': 'Quantity updated successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400




@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    per_page = 3
    # Regular rendering without search results
    blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
 #  print([blog.author for blog in blog_posts])  # Add this line for debugging
    return render_template('blog.html', blog_posts=blog_posts)

@app.route('/service1')
def courses():
    return render_template('service1.html')  

@app.route('/service2')
def mentorship():
    return render_template('service2.html')

@app.route('/team')
def team():
    return render_template('team.html') 

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')


@app.route('/team-building')
def teambuilding():
    return render_template('team-building.html')

@app.route('/blog-details')
def blog_details():
    return render_template('blog-details.html')

@app.route('/courses/course-details2')
def course_details2():
    return render_template('/courses/course-details2.html')

@app.route('/courses/course-details1')
def course_details1():
    return render_template('/courses/course-details1.html')


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

#@app.route('/sign-in', methods=['GET', 'POST'])
#def signup_signin():
#    return render_template('sign-in.html')


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


# Route to render the checkout page
@app.route('/checkout')
def checkout():
    # Retrieve cart items for the current user (similar to how it's done in the mycart route)
    user_id = current_user.id
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    # Create a defaultdict to store aggregated quantities and totals for each product
    product_totals = defaultdict(lambda: {'quantity': 0, 'total': 0})
    # Calculate total cost for all items
    total_cost = 0

# Aggregate quantities and totals for each product
    for item in cart_items:
        product_id = item.product_id
        product = Product.query.filter_by(id=product_id).first()  # Fetch product information
        product_name = product.name if product else 'Unknown' 
        product_description = product.description if product else 'Unknown'
        
        product_totals[product_id]['name'] = product_name
        product_totals[product_id]['description'] = product_description
        product_totals[item.product_id]['quantity'] += item.quantity
        product_totals[item.product_id]['total'] += item.price * item.quantity
        # Calculate total cost for all items
        total_cost += item.price * item.quantity
    # Pass cart items to the checkout template
    return render_template('checkout.html', product_totals=product_totals, total_cost=total_cost)

# Route to handle payment form submission
@app.route('/process_payment', methods=['POST'])
def process_payment():
    # Retrieve form data from the request
    token = request.form['stripeToken']
    amount = int(request.form['amount'])  # Convert amount to integer

    try:
        # Create a charge using the Stripe API
        stripe.Charge.create(
            amount=amount,
            currency='usd',
            description='Payment for purchase',
            source=token
        )
        # Payment was successful
        return jsonify({'message': 'Payment successful!'}), 200
    except stripe.error.StripeError as e:
        # Payment failed
        return jsonify({'error': str(e)}), 400



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    ssl_context = ('cert.pem', 'key.pem')
    app.secret_key = 'your_secret_key'  # Needed for flashing messages
    app.run(host='127.0.0.1', port=5002, ssl_context=('cert.pem', 'key_decrypted.pem'), debug=True)

