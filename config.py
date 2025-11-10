import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'data.sqlite')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail (fill with real values in .env for production)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # 🔒 Admin Security
    # Hashed password for better protection (use werkzeug to generate)
    ADMIN_PASSWORD_HASH = os.environ.get(
    'ADMIN_PASSWORD_HASH',
    'scrypt:32768:8:1$5krR6wNY2z4Zr9Ob$a999462018940f5e9650327299cca44d997aa1deed71d19ea8a69b42133a9c8a62c2e09cb7c6d3c9d36bb3119d16176e8a04f4e5f1ada938f5ddfd8b5d0adb22'
)


    # Session timeout in seconds (e.g., 30 min)
    PERMANENT_SESSION_LIFETIME = 1800

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4MB
