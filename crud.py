from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from models import db, User, Role, Permission, Project
from itsdangerous import URLSafeTimedSerializer
from flask import url_for
import uuid
import secrets
import logging
import werkzeug.security
logging.basicConfig(filename='app_operations.log', level=logging.INFO)

class CRUD:
    @staticmethod
    def add_project(model, name, description, status):
        try:
            existing_project = model.query.filter_by(name=name).first()
            if existing_project:
                logging.info(f"Project with name '{name}' already exists.")
                return {"status": "error", "message": "Error: A project with this name already exists."}
            
            new_project = model(name=name, description=description, status=status)
            db.session.add(new_project)
            db.session.commit()
            
            logging.info(f"Added new {model.__name__} with name: {name}")
            return {"status": "success", "message": "Project added successfully!"}
        
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error adding {model.__name__}: {e}")
            return {"status": "error", "message": "Database error: Unable to add project."}
    
    @staticmethod
    def view_project_by_id(model, project_id):
        """Fetch a single project by ID."""
        project = model.query.get(project_id)
        if not project:
            return None  
        
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status
        }
    
    
    
    @staticmethod
    def edit_project(project_id, updates):
        """Edits project details including checks for project name duplication."""
        try:
            project = Project.query.get(project_id)
            if not project:
                print("❌ Error: Project not found.")
                return False, "Error: Project not found."
            
            new_name = updates.get("name")
            if new_name:
                existing_project = Project.query.filter(Project.name == new_name, Project.id != project_id).first()
                if existing_project:
                    print("❌ Error: Project name already in use.")
                    return False, "Error: A project with this name already exists."
            
            updated_fields = []
            
            for field in ["name", "description", "status"]:
                new_value = updates.get(field)
                if new_value and new_value.strip() and getattr(project, field) != new_value:
                    setattr(project, field, new_value)
                    updated_fields.append(f"{field}: {new_value}")
            
            if updated_fields:
                print(f"📌 Updated Fields: {updated_fields}")
                print(f"📌 Final Project Data: Name: {project.name}, Description: {project.description} , Status: {project.status}")
            
            db.session.commit()
            print("✅ Changes committed successfully!")
            
            return True, "Project updated successfully!"
        
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"❌ Database error: {e}")
            return False, f"Database error: {str(e)}"
        
        
    @staticmethod
    def add_user(name, email, password, role_name):
        try:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {"status": "error", "message": "Email already exists. Please use a different email."}
            
            hashed_password = generate_password_hash(password, method="scrypt")
            
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                return {"status": "error", "message": "Invalid role. Please select a valid role."}
            
            activation_token = secrets.token_urlsafe(32)
            
            new_user = User(
                name=name,
                email=email,
                password_hash=hashed_password,
                fs_uniquifier=secrets.token_hex(16),
                is_active=False,
                activation_token=activation_token
            )
            new_user.roles.append(role)
            
            db.session.add(new_user)
            db.session.commit()
            
            activation_link = url_for('activate_account', token=activation_token, _external=True)
            
            CRUD.send_email(new_user.email, "Activate Your Account", f"Click here to activate your account: {activation_link}")
            
            return {
                "status": "success",
                "message": "User added successfully. Activation email sent.",
                "activation_link": activation_link
            }
        
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
    
    
    def send_email(to_email, subject, body):
        print(f"📧 Sending email to: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")   
    
   
        
    @staticmethod
    def edit_user(user_id, updates):
        """Edits user details including role."""
        try:
            user = User.query.get(user_id)
            if not user:
                print("❌ Error: User not found.")
                return False, "Error: User not found."
            
            new_email = updates.get("email")
            if new_email:
                existing_user = User.query.filter(User.email == new_email, User.id != user_id).first()
                if existing_user:
                    print("❌ Error: Email already in use.")
                    return False, "Error: Email is already in use."
            
            new_role_name = updates.get("role")
            if new_role_name:
                new_role = Role.query.filter_by(name=new_role_name).first()
                if new_role:
                    user.roles = [new_role]  # Replace existing roles
                    print(f"✅ Updated role to: {new_role_name}")
                else:
                    print(f"⚠️ Role '{new_role_name}' not found.")
            
            updated_fields = []
            for field in ["name", "email"]:
                new_value = updates.get(field)
                if new_value and new_value.strip() and getattr(user, field) != new_value:
                    setattr(user, field, new_value)
                    updated_fields.append(f"{field}: {new_value}")
            
            print(f"📌 Updated Fields: {updated_fields}")
            print(f"📌 Final User Data: Name: {user.name}, Email: {user.email}, Roles: {[role.name for role in user.roles]}")
            
            db.session.commit()
            print("✅ Changes committed successfully!")
            
            return True, "User updated successfully!"
        
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"❌ Database error: {e}")
            return False, f"Database error: {str(e)}"
    
    @staticmethod
    def delete_record(model, record_id):
        try:
            record = model.query.get(record_id)
            if record:
                db.session.delete(record)
                db.session.commit()
                logging.info(f"Deleted {model.__name__} with ID {record_id}")
                return True, "Item deleted successfully!"
            else:
                return False, "Error: Record not found."
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error deleting {model.__name__} with ID {record_id}: {e}")
            return False, f"Error deleting item: {str(e)}"

    @staticmethod
    def modify_permission(role_id, permission_id, action):
        """
        Modify a role's permissions.
        :param role_id: The role ID to modify.
        :param permission_id: The permission ID to add/remove.
        :param action: "add" to grant, "remove" to revoke.
        :return: Success or error message.
        """
        try:
            role = Role.query.get(role_id)
            permission = Permission.query.get(permission_id)
            
            if not role or not permission:
                return {"status": "error", "message": "Role or Permission not found."}
            
            if action == "add":
                if permission not in role.permissions:
                    role.permissions.append(permission)
                    db.session.commit()
                    return {"status": "success", "message": f"Permission '{permission.name}' added to '{role.name}'."}
                else:
                    return {"status": "error", "message": "Permission already exists."}

            elif action == "remove":
                if permission in role.permissions:
                    role.permissions.remove(permission)
                    db.session.commit()
                    return {"status": "success", "message": f"Permission '{permission.name}' removed from '{role.name}'."}
                else:
                    return {"status": "error", "message": "Permission does not exist."}

            return {"status": "error", "message": "Invalid action."}
        
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error modifying permissions: {e}")
            return {"status": "error", "message": str(e)}

