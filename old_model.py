from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()  # ✅ Define db instance here, initialized later in app.py

roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))  
    active = db.Column(db.Boolean, default=True)
    
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }
