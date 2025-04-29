import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    blog_id = db.Column(db.Integer, nullable=False)
    

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(String)
    content = db.Column(String)
    author = db.Column(String)
    date = db.Column(String)
    keywords = db.relationship('Keyword', back_populates='blog_post')
    
class Keyword(db.Model):
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    blog_post = relationship('BlogPost', back_populates='keywords')
    
class Subscriber(db.Model):
    __tablename__ = 'subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    signup_date = db.Column(db.DateTime, default=datetime.now)
    active = db.Column(db.Boolean, default=True)
    
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    signup_date = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=False)

    
    def is_authenticated(self):
        return True  # You can customize this method based on your authentication logic

    def is_active(self):
        return True  # You can customize this method based on your activation logic

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
    
    
    # Add more columns as needed