import os
import logging
import json
import shutil
from flask import render_template, request, redirect, url_for, session, jsonify, make_response
from flask_wtf.csrf import generate_csrf, validate_csrf
from models import db, User, Role, Permission, UserPermissions, UserRoles
from werkzeug.security import check_password_hash
from crud import CRUD
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import set_message, get_message

def init_routes(app):
    @app.before_request
    def prevent_session_before_login():
        """Prevents session from being created before login."""
        if "user_id" not in session:
            return  
        
    @app.route("/", methods=["GET", "POST"])
    def login_page():
        message = get_message()

        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password_hash, password):
                session.clear()
                session["user_id"] = user.id
                session["roles"] = [role.name for role in user.roles] if user.roles else []
                session["_fresh"] = True
                
                # ✅ Generate CSRF token **only after login**
                session["csrf_token"] = generate_csrf()

                session.permanent = True
                session.modified = True
                
                set_message("Login successful!")
                return redirect(url_for("index"))
            
            set_message("Invalid email or password")
            return redirect(url_for("login_page"))
        
        return render_template("login.html", message=message)
    
    @app.route("/check-session")
    def check_session():
        """Returns the current session data for debugging."""
        return jsonify(
            {
                "user_id": session.get("user_id"),
                "roles": session.get("roles"), 
                "csrf_token": session.get("csrf_token"),
                "session_permanent": session.permanent,
            }
        )
    
    @app.route("/index")
    def index():
        """Main index page after login."""
        if "user_id" not in session:
            set_message("Login required!")  # ✅ Set the message before redirecting
            return redirect(url_for("login_page"))
        
        user_roles = session.get("roles", [])  # ✅ Fetch roles correctly
        role = user_roles[0] if user_roles else "Guest"  # Default to "Guest" if no role
        
        message = get_message()  # ✅ Retrieve the message
        
        return render_template("index.html", user_roles=user_roles, role=role, message=message)
    
    @app.route("/logout")
    def logout():
        """Forcefully clear session and delete session files."""
        session.clear()  # ✅ Clear session
        
        # ✅ Delete session files in Flask-Session
        session_dir = app.config["SESSION_FILE_DIR"]
        try:
            for file in os.listdir(session_dir):
                os.remove(os.path.join(session_dir, file))
        except Exception as e:
            print(f"⚠️ Error deleting session file: {e}")
        
        # ✅ Expire session cookie
        response = redirect(url_for("login_page"))
        response.set_cookie("flask_session", "", expires=0, path="/")
        
        return response
        
    
    @app.route("/user-management")
    def user_management():
        search_query = request.args.get('search', '')
        
        db.session.expire_all()  # Ensure fresh data from DB
        
        if search_query:
            users = User.query.filter(User.name.like(f"%{search_query}%")).all()
        else:
            users = User.query.all()
        
        # ✅ Fetch logged-in user's permissions
        user_id = session.get("user_id")
        
        user_perms = []
        
        if user_id:
            user_perms = db.session.query(Permission.name)\
                .join(UserPermissions, Permission.id == UserPermissions.permission_id)\
                .filter(UserPermissions.user_id == user_id).all()
            user_perms = [perm[0] for perm in user_perms]  # Extract permission names
        
        # ✅ Fetch user roles & permissions for each user in the table
        user_data = []
        for user in users:
            roles = db.session.query(Role.name)\
                .join(UserRoles, Role.id == UserRoles.role_id)\
                .filter(UserRoles.user_id == user.id).all()
            roles = [role[0] for role in roles]  # Extract role names
            
            permissions = db.session.query(Permission.name)\
                .join(UserPermissions, Permission.id == UserPermissions.permission_id)\
                .filter(UserPermissions.user_id == user.id).all()
            permissions = [perm[0] for perm in permissions]  # Extract permission names
            
            user_data.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "roles": roles,
                "permissions": permissions
            })
        
        message = get_message()
        return render_template(
            'modules/user_management.html',
            user_data=user_data,  # ✅ Now passing user data correctly
            user_perms=user_perms,  # ✅ Logged-in user's permissions
            message=message
        )
    
    
    
  
    @app.route("/load_module/<module>")
    def load_module(module):
        """Loads a module dynamically and includes user roles."""
        user_roles = session.get("roles", [])
        
        print(f"🔍 Flask: Requested module -> {module}")  # Debugging
        
        if module == "user_management":
            users = User.query.all()
            user_permissions = {}
            
            for user in users:
                perms = db.session.query(Permission.name) \
                    .join(UserPermissions, Permission.id == UserPermissions.permission_id) \
                    .filter(UserPermissions.user_id == user.id).all()
                user_permissions[user.id] = [perm[0] for perm in perms]

            print(f"👥 Fetching {len(users)} users for User Management")  # Debugging
            return make_response(render_template("modules/user_management.html", users=users, user_roles=user_roles, user_permissions=user_permissions))
        
        # Allow only valid modules to prevent security issues
        allowed_modules = {"dashboard", "crm", "marketing", "leads", "employees", "user_management"}
        if module not in allowed_modules:
            print(f"❌ Flask: Invalid module {module}")  # Debugging
            return "<h2>Invalid Module</h2>", 404
        
        # Check if the template file exists
        template_path = f"modules/{module}.html"
        if not os.path.isfile(os.path.join(app.template_folder, template_path)):
            print(f"❌ Flask: Module {module} template not found")  # Debugging
            return "<h2>Module Not Found</h2>", 404
        
        print(f"✅ Flask: Found module template -> {template_path}")  # Debugging
        response = make_response(render_template(template_path, user_roles=user_roles, active_module=module))
        
        # Prevent caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
        
    
    @app.route("/items", methods=["GET"])
    def get_items():
        """Returns a list of items."""
        if "user_id" not in session:
            return jsonify({"message": "Unauthorized"}), 403
        
        items = CRUD.view_item(Item, order_by=Item.id.desc())  
        return jsonify(items or [])
    
    @app.route('/add_user', methods=['GET', 'POST'])
    def add_user():
        if request.method == "GET":
            return render_template("modules/add_user.html", message=get_message())
        
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not all([name, email, password, role]):
            set_message("All fields are required.")
            return render_template("modules/add_user.html", message=get_message())
        
        result = CRUD.add_user(name, email, password, role)
        set_message(result['message'])
        
        return render_template("modules/add_user.html", message=get_message())
        
    @app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
    def edit_user(user_id):
        if "admin" not in session.get("roles", []):
            return jsonify({"error": "Unauthorized"}), 403  # Return JSON for AJAX
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404  # Return JSON for AJAX
        
        
        if request.method == "POST":
            updates = {
                "name": request.form.get("name"),
                "email": request.form.get("email"),
                "role": request.form.get("role")
            }
            print(f"🔍 Received updates: {updates}") 
            
            selected_permissions = request.form.getlist("permissions")
            print(f"🔍 Selected permissions for update: {selected_permissions}")  
            
            try:
                success, message = CRUD.edit_user(user_id, updates, selected_permissions)
                if not success:
                    return jsonify({"error": message}), 400  # Return JSON for AJAX
                
                return jsonify({"success": True, "redirect_url": url_for('index', module='user_management')})  
            
            except IntegrityError as e:
                return jsonify({"error": f"Database error: {str(e)}"}), 400  # Return JSON for AJAX
        
        # Extract the user's current role (assuming one role per user)
        user_role = user.roles[0].name if user.roles else None  
        
        # ✅ Fetch permissions assigned directly to the user
        current_permissions = (
            db.session.query(UserPermissions.permission_id)
            .filter_by(user_id=user.id)
            .all()
        )
        
        # Convert from list of tuples to a flat list of permission IDs
        current_permissions = [perm[0] for perm in current_permissions]
        print("Raw SQLAlchemy Result:", current_permissions)
        
        print("Current Permissions:", current_permissions)  # Debugging
        
        # Fetch all available permissions (for displaying checkboxes)
        available_permissions = Permission.query.all()
        print("Available Permissions:", [(p.id, p.name) for p in available_permissions])  # Debugging
        
        return render_template(
            "modules/edit_user.html",
            user=user,
            user_role=user_role,
            current_permissions=current_permissions,
            available_permissions=available_permissions
        )  
    
    
    
    
        
        
        
    
    
    
    
    
    @app.route('/delete_user/<int:user_id>', methods=['POST'])
    def delete_user(user_id):
        if "admin" not in session.get("roles", []):
            set_message("Unauthorized")
            return jsonify({"success": False, "message": get_message()}), 403
        
        user = User.query.get(user_id)
        if not user:
            set_message("User not found")
            return jsonify({"success": False, "message": get_message()}), 404
        
        CRUD.delete(user)  # Delete the user
        users = User.query.all()  # Fetch updated user list

        # ✅ Wrap response in userTableContainer for JavaScript to parse correctly
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            set_message("User deleted successfully!")
            return f"""
            <div id="userTableContainer">
                {render_template("modules/partials/user_table.html", users=users)}
            </div>
            """
        
        set_message("User deleted successfully!")
        return redirect(url_for("user_management"))
    
        
    @app.route("/add", methods=["POST"])
    def add_item():
        if "admin" not in session.get("roles", []):
            return "Unauthorized", 403
        
        item_name = request.form.get("name")
        if not item_name:
            session["error_message"] = "Item name is required"
            return redirect(url_for("index"))
        
        data = {"name": item_name}
        success, message = CRUD.add(Item, data)

        if not success:
            session["error_message"] = message  
        
        return redirect(url_for("index", message=message))  
        
    @app.route("/item/<int:item_id>", methods=["GET"])
    def view_item(item_id):
        """Render the View Item page."""
        if "user_id" not in session:
            return redirect(url_for("login_page", login_required=True))
        
        item = CRUD.view_item(Item, filters={"id": item_id})
        if item:
            return render_template("view_item.html", item=item[0])  
        return redirect(url_for("index"))  
    
    @app.route("/item", methods=["POST"])
    def create_item():
        """Creates a new item (Admin only)."""
        if "admin" not in session.get("roles", []):
            return jsonify({"message": "Unauthorized"}), 403

        submitted_token = request.form.get("csrf_token")
        if not validate_csrf(submitted_token):
            return jsonify({"message": "CSRF validation failed"}), 400
        
        data = request.form.to_dict()
        success, message = CRUD.add(Item, data)
        return jsonify({"success": success, "message": message}), 201 if success else 400
    
    @app.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
    def update_item(item_id):
        """Updates an item (Admin only)."""
        if "admin" not in session.get("roles", []):
            return redirect(url_for("index", message="Unauthorized"))

        item = Item.query.get(item_id)
        if not item:
            return redirect(url_for("index", message="Item not found"))

        if request.method == "POST":
            data = request.form.to_dict()
            success, message = CRUD.update(item, data)
            if success:
                return redirect(url_for("index", message=message))  
            else:
                return render_template("update_item.html", item=item, error=message)  

        return render_template("update_item.html", item=item)
        
    @app.route('/delete/<int:item_id>', methods=['POST'])
    def delete_item(item_id):
        if "admin" not in session.get("roles", []):
            return redirect(url_for("index", message="Unauthorized"))

        try:
            item = db.session.query(Item).filter_by(id=item_id).first()
            if not item:
                return redirect(url_for('index', message="Item not found"))

            db.session.delete(item)
            db.session.commit()

            return redirect(url_for('index', message="Item deleted successfully!"))
        
        except Exception as e:
            db.session.rollback()  
            logging.error(f"Error deleting Item: {e}")
            return redirect(url_for('index', message=f"Error deleting item: {str(e)}"))
        
    @app.route('/crm')
    def crm():
        return render_template("modules/crm.html")
    
    @app.route('/employees')
    def employees():
        return render_template("modules/employees.html")
    
    @app.route('/leads')
    def leads():
        return render_template("modules/leads.html")
    
    @app.route('/marketing')
    def marketing():
        return render_template("modules/marketing.html")
    

