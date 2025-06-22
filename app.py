import os
import logging
import traceback
from flask import Flask, session, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from flask_session import Session
from datetime import timedelta
from flask_security.utils import hash_data
from helpers.helpers import get_message 

app = Flask(__name__)

app.config["DEBUG"] = True
app.config["ENV"] = "development"

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

@app.context_processor
def inject_message():
    """Make messages globally available in templates."""
    return {'message': get_message()}

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///prokora.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = os.urandom(24)
app.config["SECURITY_PASSWORD_SALT"] = "salted"

app.config["SECURITY_LOGIN_URL"] = "/login"
app.config["SECURITY_POST_LOGIN_VIEW"] = "/index"
app.config["SECURITY_LOGOUT_URL"] = "/logout"
app.config["SECURITY_POST_LOGOUT_VIEW"] = "/"

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_NAME"] = "flask_session"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_REFRESH_EACH_REQUEST"] = False
app.config["SESSION_PERMANENT"] = False
app.permanent_session_lifetime = timedelta(days=1)

Session(app)  # Initialize Flask-Session

from models import db, User, Role  

db.init_app(app)
migrate = Migrate(app, db)

# ✅ Register Routes
from routes import init_routes  
init_routes(app)

@app.before_request
def prevent_session_creation():
    """Prevent Flask from creating a session before login."""
    if "user_id" not in session:
        session.modified = False  

@app.template_test("intersecting")
def is_intersecting(list1, list2):
    try:
        return bool(set(list1) & set(list2))
    except Exception:
        return False
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    
    app.run(host="0.0.0.0", port=5000, debug=True)
