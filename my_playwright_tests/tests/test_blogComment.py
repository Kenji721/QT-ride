import pytest
import time
from playwright.sync_api import sync_playwright
import os
import sys

# Assuming your models and Flask app setup are in the 'app.py' at the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import app, db  # Adjust this import according to your actual app setup
from models import Comment  # Assuming Comment is defined in models.py which is importable from app

@pytest.fixture(scope='session')
def app_context():
    """Create a Flask application context for the tests."""
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"  # Use in-memory database for tests
    })
    with app.app_context():
        db.create_all()  # Create all database tables
        yield app
        db.session.remove()


@pytest.fixture(scope='session')
def playwright():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope='session')
def browser(playwright):
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()

@pytest.fixture
def context(browser):
    context = browser.new_context(ignore_https_errors=True)
    yield context
    context.close()

@pytest.fixture
def page(context):
    page = context.new_page()
    yield page
    page.close()

def test_navigation(page, app_context):
  with app.app_context():
    """Test navigating to a specific blog and interacting with a comment form."""
    page.goto('http://127.0.0.1:5002/blogs/5', wait_until="domcontentloaded")
    # Assuming '#exampleFormControlInput1' is the ID for the name input field
    page.wait_for_selector('#exampleFormControlInput1', state='visible')
    page.fill('#exampleFormControlInput1', 'Rami Levi')

    # Email
    page.fill('input[placeholder="Your Email"]', 'levi.rami@gmail.com')

    # Message
    page.fill('textarea[placeholder="Your Message"]', '4')

    # Submit the form
    page.click('role=button[name="Comment"]')

    # Clean up: Remove the comment from the database
    with app.app_context():
        comment = Comment.query.filter_by(name="Rami Levi", email="levi.rami@gmail.com", message="4").first()
        if comment:
            db.session.delete(comment)
            db.session.commit()
    
    # Check for presence of the previous comments
    assert page.text_content('div.col-md-9.justify-content-center h5') == 'Rami Levi'
    assert page.text_content('div.col-md-9.justify-content-center p') == '1'
    time.sleep(3)  