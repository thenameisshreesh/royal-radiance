import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this-secret')
    
    # ✅ Use cloud DB if provided, otherwise use /tmp for writable SQLite on Vercel
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:////tmp/data.sqlite'  # 4 slashes for absolute path
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    ADMIN_PASSWORD_HASH = os.environ.get(
        'ADMIN_PASSWORD_HASH',
        'scrypt:32768:8:1$5krR6wNY2z4Zr9Ob$a999462018940f5e9650327299cca44d997aa1deed71d19ea8a69b42133a9c8a62c2e09cb7c6d3c9d36bb3119d16176e8a04f4e5f1ada938f5ddfd8b5d0adb22'
    )

    PERMANENT_SESSION_LIFETIME = 1800

    # ✅ Use /tmp/uploads for writable files on Vercel
    UPLOAD_FOLDER = os.environ.get(
        'UPLOAD_FOLDER',
        os.path.join('/tmp', 'uploads')  # writable folder
    )
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4MB
