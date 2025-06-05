from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
import uuid

db = SQLAlchemy()

# Association Tables
role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True)
)

module_roles = db.Table(
    "module_roles",
    db.Column("module_id", db.Integer, db.ForeignKey("module.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id", ondelete="CASCADE"), primary_key=True)
)

submodule_roles = db.Table(
    "submodule_roles",
    db.Column("submodule_id", db.Integer, db.ForeignKey("submodule.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id", ondelete="CASCADE"), primary_key=True)
)

# Role Model
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    permissions = db.relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = db.relationship("User", secondary="user_roles", back_populates="roles")
    modules = db.relationship("Module", secondary=module_roles, back_populates="allowed_roles")
    submodules = db.relationship("Submodule", secondary=submodule_roles, back_populates="allowed_roles")

    def __repr__(self):
        return f"<Role {self.name}>"

# User-Role Association
class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer, db.ForeignKey("role.id", ondelete="CASCADE"))

# Permission Model
class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    roles = db.relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission {self.name}>"

# Project Model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='on_going')

    def __repr__(self):
        return f"<Project {self.name}>"

# Module Model
class Module(db.Model):
    __tablename__ = "module"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255))
    sequence = db.Column(db.Integer, default=0, nullable=False)

    allowed_roles = db.relationship("Role", secondary=module_roles, back_populates="modules")
    submodules = db.relationship("Submodule", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module {self.name}>"

# Submodule Model
class Submodule(db.Model):
    __tablename__ = "submodule"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255))
    sequence = db.Column(db.Integer, default=0, nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id', ondelete='CASCADE'), nullable=False)
    
    module = db.relationship("Module", back_populates="submodules")
    allowed_roles = db.relationship("Role", secondary=submodule_roles, back_populates="submodules")
    
    def __repr__(self):
        return f"<Submodule {self.name}>"

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    is_active = db.Column(db.Boolean, default=False)
    activation_token = db.Column(db.String(64), unique=True)

    roles = db.relationship("Role", secondary="user_roles", back_populates="users")

    @property
    def inherited_permissions(self):
        permissions = set()
        for role in self.roles:
            permissions.update(role.permissions)
        return permissions

    @property
    def all_permissions(self):
        return self.inherited_permissions

    def __repr__(self):
        return f"<User {self.email}>"
