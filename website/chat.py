from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from .chatbot import chatbot_response,check_crisis
from .models import ChatMessage, ChatSession
from . import db

chat = Blueprint('chat', __name__)

# Route to list all chat sessions for the user
@chat.route('/chat', methods=['GET'])
@login_required
def chat_sessions():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    return render_template("chat_sessions.html", user=current_user, sessions=sessions)

# Route to create a new chat session
@chat.route('/chat/new', methods=['GET'])
@login_required
def new_chat():
    new_session = ChatSession(user_id=current_user.id, session_name="New Chat")
    db.session.add(new_session)
    db.session.commit()
    return redirect(url_for('chat.chat_page', session_id=new_session.id))

# Route to view a specific chat session
@chat.route('/chat/<int:session_id>', methods=['GET'])
@login_required
def chat_page(session_id):
    # Ensure the session belongs to the current user.
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    messages = ChatMessage.query.filter_by(chat_session_id=session_id).order_by(ChatMessage.timestamp).all()
    return render_template("chat.html", user=current_user, messages=messages, session_id=session_id)

# Route to handle chat responses for a given session
@chat.route('/chat-response/<int:session_id>', methods=['POST'])
@login_required
def chat_response(session_id):
    # Retrieve the chat session for the logged-in user
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    
    data = request.get_json()
    user_input = data.get("user_input", "")
    
    # Save the user's message in the database
    user_msg = ChatMessage(chat_session_id=session_id, role='user', message=user_input)
    db.session.add(user_msg)
    db.session.commit()
    
    # Check if the input indicates a crisis
    if check_crisis(user_input):
        crisis_message = (
            "It seems you're in significant distress. If you're in immediate danger, please call your local emergency services immediately. "
            "For those in the United States, please click <a href='tel:911'>here</a> to call 911 immediately. "
            "Alternatively, if you need professional support, click <a href='https://esanjeevani.mohfw.gov.in/#/' target='_blank'>here</a> to connect with a telehealth professional."
        )
        assistant_msg = ChatMessage(chat_session_id=session_id, role='assistant', message=crisis_message)
        db.session.add(assistant_msg)
        db.session.commit()
        return jsonify({"response": crisis_message})
    
    # Otherwise, process the message normally
    response_text = chatbot_response(user_input)
    
    # Save the chatbot's normal response in the database
    assistant_msg = ChatMessage(chat_session_id=session_id, role='assistant', message=response_text)
    db.session.add(assistant_msg)
    db.session.commit()
    
    return jsonify({"response": response_text})

# Route to delete a chat session (and its messages)
@chat.route('/chat/delete/<int:session_id>', methods=['POST'])
@login_required
def delete_chat(session_id):
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    # Delete all messages for this session
    ChatMessage.query.filter_by(chat_session_id=session_id).delete()
    db.session.delete(session)
    db.session.commit()
    flash("Chat session deleted successfully", "success")
    return redirect(url_for('chat.chat_sessions'))
