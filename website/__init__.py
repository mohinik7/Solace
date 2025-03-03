from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import sqlite3
import pytz
from datetime import datetime
from sqlalchemy import inspect
import os

# Initialize SQLAlchemy
db = SQLAlchemy()
login_manager = LoginManager()

DB_NAME = os.path.join("instance", "database.db")

# Register blueprints (import these after db is initialized)
from .auth import auth as auth_blueprint
from .chat import chat as chat_blueprint
from .mood import mood as mood_blueprint
from .video import video as video_blueprint

def check_table_exists(conn, table_name):
    """Check if a table exists in the database"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone() is not None
    cursor.close()
    return result

def create_app(config_name='development', instance_path=None):
    # Set up instance path
    instance_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
    app = Flask(__name__, instance_path=instance_folder)
    # App already created with instance_path above
    
    # Configuration
    from config.config import config as app_config
    app.config.from_object(app_config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(chat_blueprint)
    app.register_blueprint(mood_blueprint)
    app.register_blueprint(video_blueprint)
    
    # Enable SQLite foreign keys (ON DELETE CASCADE)
    @app.before_request
    def enable_foreign_keys():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
        conn.commit()
        cursor.close()

    # Create the database and tables
    with app.app_context():
        if not check_sqlite3_database_exists(DB_NAME):
            db.create_all()
            print("Created database!")

    # Add template filter for formatting datetime
    @app.template_filter('format_datetime')
    def format_datetime(value):
        ist = pytz.timezone('Asia/Kolkata')
        utc = pytz.utc
        
        # Convert naive datetime to aware datetime (assuming it's in UTC)
        if value.tzinfo is None:
            value = utc.localize(value)
        
        # Convert to IST
        ist_dt = value.astimezone(ist)
        return ist_dt.strftime("%Y-%m-%d %H:%M")

    # Define the landing page route
    @app.route('/')
    def landing():
        from .video import get_current_video
        current_video = get_current_video()
        
        # Debug information
        if current_video:
            video_path = os.path.join(app.static_folder, 'videos', current_video)
            video_exists = os.path.exists(video_path)
            print(f"Video requested: {current_video}")
            print(f"Video path: {video_path}")
            print(f"Video exists: {video_exists}")
        else:
            print("No video configured in config.json")
            # Check if config.json exists
            config_path = os.path.join(app.static_folder, 'videos', 'config.json')
            if os.path.exists(config_path):
                print(f"Config file exists at {config_path}")
                import json
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        print(f"Config content: {config}")
                except Exception as e:
                    print(f"Error reading config: {e}")
            else:
                print(f"Config file does not exist at {config_path}")
        
        return render_template('landing.html', current_video=current_video)

    # Define the index route
    @app.route('/index')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('chat.chat_sessions'))
        else:
            return redirect(url_for('landing'))

    # Lazy import the User model after the app and db are fully initialized
    from .models import User
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
        
    return app

def check_sqlite3_database_exists(db_name):
    """Check if the SQLite3 database file exists and has the expected tables"""
    try:
        # Ensure the directory exists
        db_dir = os.path.dirname(db_name)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"Created directory: {db_dir}")
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        # Check for at least one important table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
        result = cursor.fetchone() is not None
        conn.close()
        return result
    except sqlite3.Error:
        return False
