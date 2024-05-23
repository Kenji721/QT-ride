# test_config.py

import tempfile

# Use a temporary file-based SQLite database for testing
DATABASE_URI = 'sqlite:///' + tempfile.mkstemp()[1]

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = DATABASE_URI


# Other test configuration settings
DEBUG = False
SECRET_KEY = 'your-secret-key'
WTF_CSRF_ENABLED = False  # Disable CSRF protection for testing
