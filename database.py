from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create SQLAlchemy engine
engine = create_engine("sqlite:///C:/Users/xvpn/Desktop/website/qeu/site.db")
Session = sessionmaker(bind=engine)
session = Session()
db = SQLAlchemy()
migrate = Migrate()
