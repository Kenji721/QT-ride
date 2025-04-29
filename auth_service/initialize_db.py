from app import db
from models import User  # Import your models to ensure tables are created

# Create all database tables
db.create_all()
print("Database initialized successfully.")