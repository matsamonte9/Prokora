import uuid
from app import app  # Import your Flask app
from models import db, User  # Import db and User model

# Ensure the application context is set up
with app.app_context():
    # Generate activation tokens for users without one
    users = User.query.filter(User.activation_token.is_(None)).all()
    
    for user in users:
        user.activation_token = str(uuid.uuid4())

    db.session.commit()

    print("Activation tokens generated for existing users!")
