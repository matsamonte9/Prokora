from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from models import db, User, Role, UserPermissions, Permission
import uuid


import logging
import werkzeug.security
logging.basicConfig(filename='app_operations.log', level=logging.INFO)

class CRUD:
    @staticmethod
    def add(model, data):
        try:
            existing_item = model.query.filter_by(name=data.get('name')).first()
            if existing_item:
                logging.info(f"Item with name '{data['name']}' already exists.")
                return False, "Error: Item with that name already exists."
            
            new_entry = model(**data)
            db.session.add(new_entry)
            db.session.commit()
            logging.info(f"Added new {model.__name__} with data: {data}")
            return True, "Item added successfully!"
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error creating {model.__name__}: {e}")
            return False, f"Error adding item: {str(e)}"
    
    @staticmethod
    def view_item(model, filters=None, order_by=None):
        """Fetch items from the database."""
        query = model.query
        if filters:
            query = query.filter_by(**filters)
        if order_by is not None:  # ✅ Explicit check to avoid TypeError
            query = query.order_by(order_by)
        return query.all()  # ✅ Always return a list
        
    @staticmethod
    def update(instance, updates):
        try:
            # Check if name exists in another record
            if "name" in updates:
                existing_item = instance.__class__.query.filter_by(name=updates["name"]).first()
                if existing_item and existing_item.id != instance.id:  # Ensure it's not the same item
                    return False, "Error: An item with this name already exists."
            
            for key, value in updates.items():
                setattr(instance, key, value)
            
            db.session.commit()
            logging.info(f"Updated {instance.__class__.__name__} with data: {updates}")
            return True, "Item updated successfully!"
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error updating {instance.__class__.__name__}: {e}")
            return False, f"Error updating item: {str(e)}"
    
    
    @staticmethod
    def delete(instance):
        try:
            if instance not in db.session:
                instance = db.session.merge(instance)  # Attach instance if it's detached
            
            db.session.delete(instance)
            db.session.commit()
            
            return True, "Item deleted successfully!"
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error deleting {instance.__class__.__name__}: {e}")
            return False, f"Error deleting item: {str(e)}"
    
    @staticmethod
    def add_user(name, email, password, role_name):
        try:
            # Check if the email already existsss
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return {"success": False, "message": "Email already exists. Please use a different email."}
            
            # Hash the password
            hashed_password = generate_password_hash(password, method="scrypt")
            
            # Fetch the Role object from the database
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                return {"success": False, "message": "Invalid role. Please select a valid role."}
            
            # Create a new user and assign the role
            new_user = User(
                name=name,
                email=email,
                password_hash=hashed_password,
                fs_uniquifier=str(uuid.uuid4()),
                active=True
            )
            new_user.roles.append(role)  # Assign role properly
            
            db.session.add(new_user)
            db.session.commit()  # Commit the new user to the database
            
            # Now, associate permissions with the user based on the role
            for permission in role.permissions:
                user_permission = UserPermissions(user_id=new_user.id, permission_id=permission.id)
                db.session.add(user_permission)
            
            db.session.commit()  # Commit the user permissions
            return {"success": True, "message": "User added successfully"}
        
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}
   
        
    
    @staticmethod
    def edit_user(user_id, updates, selected_permissions):
        """Edits a user's details in the database, including roles and user-specific permissions."""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "Error: User not found."
            
            # Ensure the new email is not already taken by another user
            if "email" in updates:
                existing_user = User.query.filter_by(email=updates["email"]).first()
                if existing_user and existing_user.id != user_id:
                    return False, "Error: Email is already in use."

            # Apply general updates (name, email, etc.)
            for key, value in updates.items():
                setattr(user, key, value)

            # 🔹 Fetch Role-Based Permissions (should not be removed)
            role_permissions = {perm.id for role in user.roles for perm in role.permissions}
            
            # 🔹 Remove only custom user permissions (excluding role-based ones)
            db.session.query(UserPermissions).filter(
                UserPermissions.user_id == user_id,
                UserPermissions.permission_id.notin_(role_permissions)  # Exclude role-based
            ).delete()

            # 🔹 Assign only selected custom permissions (not role-based permissions)
            valid_permissions = Permission.query.filter(Permission.id.in_(selected_permissions)).all()
            for perm in valid_permissions:
                if perm.id not in role_permissions:  # Avoid duplicating role-based permissions
                    db.session.add(UserPermissions(user_id=user_id, permission_id=perm.id))
            
            db.session.commit()
            logging.info(f"Updated user {user_id} with data: {updates} and permissions: {selected_permissions}")
            return True, "User updated successfully!"

        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error updating user {user_id}: {e}")
            return False, f"Error updating user: {str(e)}"
    
        
            
            
    
    @staticmethod
    def delete_record(model, record_id):
        record = model.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
            logging.info(f"Deleted {model.__name__} with ID {record_id}")  # ✅ Added logging
            return True
        return False