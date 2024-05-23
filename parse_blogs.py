# parse_blogs.py

import os
import sys
from bs4 import BeautifulSoup
import spacy
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import logging
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
sys.path.append('./qeu/app')
from models import BlogPost, Keyword


logging.basicConfig(
    filename='parse_blogs.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add console logging
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logging.info("Starting parse_blogs.py")

# Initialize Flask application and SQLAlchemy instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/xvpn/Desktop/website/qeu/site.db'
db = SQLAlchemy(app)
# Base = declarative_base() """

# Load English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_sm")

# Function to parse HTML files and extract keywords
def parse_html(html_file):
    with open(html_file, "r", encoding="utf-8") as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    # Extract title
    title_element = soup.find("h2", class_="blog-title")
    title = title_element.get_text() if title_element else None
    # Extract content
    content_element = soup.find("div", class_="blog-post")
    content = content_element.get_text() if content_element else None
    # Tokenize the text using spaCy
    author_element = soup.find("div", class_="blog-author")
    author = author_element.get_text() if author_element else None
    
    date_element = soup.find("div", class_="blog-date")
    date = date_element.get_text() if date_element else None
    
    doc = nlp(content)
    # Extract keywords (nouns and adjectives)
    keywords = [token.text for token in doc if token.pos_ in ("NOUN", "ADJ")]
    return title, content, author, date, keywords

# Function to store keywords in the database
def store_keywords_in_db(blog_id, title, content, author, date, keywords):
    with app.app_context():
        blog_post = db.session.query(BlogPost).filter_by(id=blog_id).first()
        if not blog_post:
            blog_post = BlogPost(id=blog_id, title=title, content=content, author=author, date=date)
            db.session.add(blog_post)
        else:
            blog_post.title = title
            blog_post.content = content
            blog_post.author = author
            blog_post.date = date


        for keyword_text in keywords:
            keyword = db.session.query(Keyword).filter_by(text=keyword_text).first()
            if not keyword:
                keyword = Keyword(text=keyword_text)
            blog_post.keywords.append(keyword)

        db.session.commit()
        logging.debug("Data committed to the database.")


# Iterate through HTML files in a directory
html_dir = "templates/blogs"
for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        logging.info(f"Processing HTML file: {filename}")
        blog_id = int(filename.split(".")[0])
        html_file = os.path.join(html_dir, filename)
        title, content, author, date, keywords = parse_html(html_file)
        logging.info(f"Title: {title}")
        logging.info(f"Content: {content}")
        logging.info(f"Keywords: {keywords}")
        store_keywords_in_db(blog_id, title, content, author, date, keywords)
        logging.info("Data stored in the database.")


logging.info("parse_blogs.py completed")
# Create database tables within Flask application context
with app.app_context():
     db.create_all()