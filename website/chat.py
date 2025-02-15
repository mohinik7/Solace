# In website/chat.py (update your chat_response route)
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .chatbot import chatbot_response
from .models import ChatMessage
from . import db

chat = Blueprint('chat', __name__)

@chat.route('/chat', methods=['GET'])
@login_required
def chat_page():
    # Retrieve conversation history for the current user
    messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp).all()
    return render_template("chat.html", user=current_user, messages=messages)

@chat.route('/chat-response', methods=['POST'])
@login_required
def chat_response():
    data = request.get_json()
    user_input = data.get("user_input", "")

    # Save the user's message
    user_msg = ChatMessage(user_id=current_user.id, role='user', message=user_input)
    db.session.add(user_msg)
    db.session.commit()

    # Get chatbot response
    response_text = chatbot_response(user_input)

    # Save the assistant's message
    assistant_msg = ChatMessage(user_id=current_user.id, role='assistant', message=response_text)
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({"response": response_text})


