from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "database.db"

from .models import User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev_secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # Force SQLite to respect ON DELETE CASCADE
    with app.app_context():
        from sqlalchemy import event
        from sqlalchemy.engine import Engine

        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

    # IMPORTANT: Initialize the SQLAlchemy instance with the app
    db.init_app(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

# Register a custom filter
    @app.template_filter('to_ist')
    def to_ist_filter(value):
        if not value:
            return ""
        # If your stored datetime is naive (no tzinfo), assume it's UTC
        utc_dt = value
        if value.tzinfo is None:
            import pytz
            utc_dt = value.replace(tzinfo=pytz.utc)
        ist_tz = pytz.timezone('Asia/Kolkata')
        ist_dt = utc_dt.astimezone(ist_tz)
        return ist_dt.strftime("%Y-%m-%d %H:%M")


    # Register Blueprints
    from .auth import auth
    from .chat import chat
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(chat, url_prefix='/')

    # Define the index route
    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('chat.chat_sessions'))
        else:
            return redirect(url_for('auth.login'))

    # Initialize the LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
