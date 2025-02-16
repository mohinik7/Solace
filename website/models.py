# website/models.py
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Existing models...

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    

# New models for chat conversations:
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    session_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    # Relationship to messages (optional)
    messages = db.relationship('ChatMessage', backref='session', lazy=True)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    role = db.Column(db.String(10))  # e.g., 'user' or 'assistant'
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
