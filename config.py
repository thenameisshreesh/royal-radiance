import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this-secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database: /tmp/data.sqlite on serverless, instance/data.sqlite locally
    if os.environ.get('IS_SERVERLESS', '0') == '1':
        # Vercel or serverless environment
        os.makedirs('/tmp', exist_ok=True)
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/data.sqlite'
    else:
        INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
        os.makedirs(INSTANCE_DIR, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_DIR, 'data.sqlite')

    # Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Admin password hash
    ADMIN_PASSWORD_HASH = os.environ.get(
        'ADMIN_PASSWORD_HASH',
        'scrypt:32768:8:1$5krR6wNY2z4Zr9Ob$a999462018940f5e9650327299cca44d997aa1deed71d19ea8a69b42133a9c8a62c2e09cb7c6d3c9d36bb3119d16176e8a04f4e5f1ada938f5ddfd8b5d0adb22'
    )

    # Session
    PERMANENT_SESSION_LIFETIME = 1800

    # Upload folder (still use /tmp/uploads on serverless)
    if os.environ.get('IS_SERVERLESS', '0') == '1':
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4MB
