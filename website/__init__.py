from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .models import User, ChatSession, ChatMessage

    with app.app_context():
        db.create_all()

    # Blueprints
    from .auth import auth
    from .chat import chat
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(chat, url_prefix='/')

    # Make the root path redirect to chatbot or login if not authenticated
    @app.route('/')
    def index():
     from flask_login import current_user
     if current_user.is_authenticated:
        return redirect(url_for('chat.chat_sessions'))
     else:
        return redirect(url_for('auth.login'))

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
