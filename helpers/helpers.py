from flask import session

def set_message(message):
    """Store message in session."""
    session['message'] = message

def get_message():
    """Retrieve and clear message from session."""
    message = session.pop('message', None)
    return message

