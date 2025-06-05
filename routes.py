import os
import logging
import json
import shutil
import secrets 
import requests
from flask import render_template, request, redirect, url_for, session, jsonify, make_response, abort
from flask_wtf.csrf import generate_csrf, validate_csrf
from models import db, User, Role, Permission, UserRoles, role_permissions, Project, Module, Submodule
from werkzeug.security import check_password_hash
from crud import CRUD
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import joinedload
from sqlalchemy import text
from helpers.helpers import set_message, get_message
from helpers.module_utils import get_accessible_modules_with_submodules
from helpers.utils import permission_required


logging.basicConfig(level=logging.DEBUG)

def init_routes(app):
    @app.before_request
    def prevent_session_before_login():
        """Prevents session from being created before login."""
        if "user_id" not in session:
            return  
    
    @app.route("/", methods=["GET", "POST"])
    def login_page():
        """Login page for the user."""
        if "user_id" in session:
            return redirect(url_for("index"))
        
        message = get_message()
        
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            
            if user:
                if not user.is_active: 
                    set_message("Account not activated. Please activate your account first.")
                    return redirect(url_for("login_page"))
                
                if check_password_hash(user.password_hash, password):
                    session.clear()
                    session["user_id"] = user.id
                    session["user_name"] = user.name
                    session["roles"] = [role.name.lower() for role in user.roles] if user.roles else []
                    session["_fresh"] = True
                    session["csrf_token"] = generate_csrf()
                    session.permanent = True
                    
                    # 🔹 Store Permissions in Session
                    roles = Role.query.filter(db.func.lower(Role.name).in_(session["roles"])).all()
                    
                    session["user_permissions"] = {perm.name for role in roles for perm in role.permissions}
                    
                    session.modified = True 
                    print("ROLES in session:", session.get("roles"), type(session.get("roles")))
                    
                    print(f"🔑 Stored Permissions in Session: {session['user_permissions']}") 
                    
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
                "user_name": session.get("user_name"),
                "roles": session.get("roles"), 
                "csrf_token": session.get("csrf_token"),
                "session_permanent": session.permanent,
            }
        )
    
    @app.route("/index", methods=["GET", "POST"])
    def index():
        """Main index page after login."""
        if "user_id" not in session:
            set_message("Login required!")
            return redirect(url_for("login_page"))
        
        user_id = session.get('user_id') 
        user_roles = session.get("roles", [])
        user_permissions = session.get("user_permissions", set())  
        
        if isinstance(user_permissions, set):  
            user_permissions = list(user_permissions)
        
        message = get_message()
        
        # ✅ Use your utility function here
        module_data = get_accessible_modules_with_submodules(user_id)
        
        accessible_modules = [module["name"] for module in module_data if not module["submodules"]]
        parent_modules = [module for module in module_data if module["submodules"]]
        
        # Convert submodules into a dict like { module_name: [list of submodules] }
        submodules = {
            module["name"]: module["submodules"]
            for module in parent_modules
        }
        
        print(f"🔑 Accessible Modules: {accessible_modules}")
        print(f"🔑 Parent Modules: {[mod['name'] for mod in parent_modules]}")
        print(f"🔑 Submodules: {submodules}")
        
        return render_template(
            "index.html",
            modules=module_data,  # Pass full module data (including submodules)
            parent_modules=parent_modules,
            submodules=submodules,
            user_roles=user_roles,
            message=message,
            user_permissions=user_permissions,
            user_id=user_id
        )
        
    
        
        
    
        
    @app.route("/logout")
    def logout():
        """Forcefully clear session and delete session files."""
        session.clear() 
        
        session_dir = app.config["SESSION_FILE_DIR"]
        try:
            for file in os.listdir(session_dir):
                os.remove(os.path.join(session_dir, file))
        except Exception as e:
            print(f"⚠️ Error deleting session file: {e}")
        
        response = redirect(url_for("login_page"))
        response.set_cookie("flask_session", "", expires=0, path="/")
        
        return response
        
    
    @app.route("/user-management")
    @permission_required(required_roles=["admin"])
    def user_management():
        search_query = request.args.get('search', '')
        
        db.session.expire_all()  
        
        if search_query:
            users = User.query.filter(User.name.like(f"%{search_query}%")).all()
        else:
            users = User.query.all()

        user_id = session.get("user_id")
        
        user_perms = []
        user_roles = []  
        
        if user_id:
            user_roles = db.session.query(Role.name)\
                .join(UserRoles, Role.id == UserRoles.role_id)\
                .filter(UserRoles.user_id == user_id).all()
            user_roles = [role[0] for role in user_roles]  
            
            permissions = set()
            for role in user_roles:
                role_obj = Role.query.filter_by(name=role).first()
                if role_obj:
                    permissions.update([perm.name for perm in role_obj.permissions])
            
            user_perms = list(permissions)  
        
        user_data = []
        for user in users:
            user_roles_data = db.session.query(Role.name)\
                .join(UserRoles, Role.id == UserRoles.role_id)\
                .filter(UserRoles.user_id == user.id).all()
            user_roles_data = [role[0] for role in user_roles_data]  
            
            permissions = set()
            for role in user_roles_data:
                role_obj = Role.query.filter_by(name=role).first()
                if role_obj:
                    permissions.update([perm.name for perm in role_obj.permissions])
            
            user_data.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "roles": user_roles_data,  
                "permissions": list(permissions)  
            })
        
        all_roles = Role.query.all()
        
        message = get_message()
        return render_template(
            'modules/user_management.html',
            user_data=user_data,  
            user_perms=user_perms,  
            message=message,
            roles=all_roles  
        )
    
    
    @app.route("/load_module/<module>/<submodule>")
    @app.route("/load_module/<module>")  # Handle cases where submodule is not passed
    def load_module(module, submodule=None):
        """Loads a module dynamically and includes user roles and submodules."""
        
        allowed_modules = ['dashboard', 'projects', 'user_management', 'crm', 'marketing', 'leads', 'employees']
        accessible_modules = ['dashboard', 'projects', 'user_management', 'crm', 'marketing', 'leads', 'employees']
        parent_modules = ['projects', 'user_management']
        
        user_roles = session.get("roles", [])
        user_permissions = session.get("user_permissions", [])
        
        module_access = {
            "user_management": {"roles": ["admin"]},
            "projects": {"roles": ["admin", "project"]},
            "crm": {"roles": ["admin", "sales"]},
            "marketing": {"roles": ["admin", "marketing"]},
            "leads": {"roles": ["admin", "leads"]},
            "employees": {"roles": ["admin"]},
        }
        
        access = module_access.get(module)
        if access:
            has_role = any(role in user_roles for role in access.get("roles", []))
            has_perm = any(perm in user_permissions for perm in access.get("permissions", []))
            if not (has_role or has_perm):
                return abort(403)  # ❌ Forbidden
        
        message = get_message()

        # Ensure session permissions are initialized
        if "user_permissions" not in session:
            roles = Role.query.filter(Role.name.in_(user_roles)).all()
            user_permissions_set = set()
            for role in roles:
                permissions = db.session.query(Permission.name) \
                    .join(Role.permissions) \
                    .filter(Role.id == role.id) \
                    .all()
                user_permissions_set.update([perm.name for perm in permissions])
            session["user_permissions"] = list(user_permissions_set)
            session.modified = True
        
        user_permissions = session["user_permissions"]
        
        # 🧩 Handle "projects" module and its submodules
        if module == "projects":
            if submodule and submodule in ["ongoing", "finished"]:
                title = submodule.capitalize()
                projects = Project.query.filter_by(status=submodule).all()
                return make_response(render_template(
                    "modules/partials/project_table.html",
                    projects=projects,
                    user_roles=user_roles,
                    user_permissions=user_permissions,
                    message=message,
                    title=title
                ))
            
            projects = Project.query.all()
            return make_response(render_template(
                "modules/projects.html",
                projects=projects,
                user_roles=user_roles,
                user_permissions=user_permissions,
                message=message
            ))

        # 🧩 Handle "user_management" full and partial loads
        if module == "user_management":
            users = User.query.all()

            user_roles_map = {}
            user_permissions_map = {}

            for user in users:
                roles = db.session.query(Role.name) \
                    .join(UserRoles, Role.id == UserRoles.role_id) \
                    .filter(UserRoles.user_id == user.id).all()
                roles = [role[0] for role in roles]
                user_roles_map[user.id] = roles

                permissions = set()
                for role in roles:
                    role_obj = Role.query.filter_by(name=role).first()
                    if role_obj:
                        permissions.update([perm.name for perm in role_obj.permissions])
                user_permissions_map[user.id] = list(permissions)
            
            # 🔁 Return partial table if submodule = user_list
            if submodule == "user_list":
            # Return full user_management.html with user list visible and permissions hidden
                return make_response(render_template(
                    "modules/user_management.html",
                    users=users,
                    user_roles=user_roles_map,
                    user_permissions=user_permissions_map,
                    message=message,
                    initial_view="user_list"  # Pass flag to show user list initially
                ))
            

            # 🧾 Otherwise, return full user_management view
            return make_response(render_template("modules/user_management.html",
                                                users=users,
                                                user_roles=user_roles_map,
                                                user_permissions=user_permissions_map,
                                                message=message))
        
        # 📦 Handle general modules
        if module not in allowed_modules:
            return "<h2>Invalid Module</h2>", 404
        
        template_path = f"modules/{module}.html"
        if not os.path.isfile(os.path.join(app.template_folder, template_path)):
            return "<h2>Module Not Found</h2>", 404
        
        response = make_response(render_template(
            template_path,
            user_roles=user_roles,
            active_module=module,
            message=message,
            accessible_modules=accessible_modules,
            parent_modules=parent_modules
        ))
        
        # Prevent caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    
    @app.route("/user/view/<int:user_id>")
    def view_user_profile(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.roles[0].name if user.roles else None  # ✅ safe access
        }
        
        return jsonify({"status": "success", "user": user_data})
        
    
    @app.route('/user/edit_profile/<int:user_id>', methods=['POST'])
    def edit_user_profile(user_id):
        if session.get("user_id") != user_id:
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        updates = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
        }

        print(f"📝 Profile update received: {updates}")
        success, message = CRUD.edit_user(user_id, updates)
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            if success:
                 # Update session if the logged-in user changed their own name/email
                if session.get("user_id") == user_id:
                    session["user_name"] = updates.get("name", session.get("user_name"))
                    session["email"] = updates.get("email", session.get("email"))
                
                return jsonify({"status": "success", "message": "Profile updated"})
            else:
                return jsonify({"status": "error", "message": message})
        
        set_message(message)
        return redirect(url_for("index", module="dashboard"))
    
    
    
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
        
        if result['status'] == 'success':
            activation_link = result['activation_link']  
            print(f"🔗 Activation Link: {activation_link}") 
            
            # Redirect with module and submodule query parameters
            return redirect(url_for('index', module='user_management', submodule='user_list'))
        
        return render_template("modules/add_user.html", message=get_message())
    
    
    @app.route('/activate/<token>', methods=['GET'])
    def activate_account(token):
        """Activates user account if the activation token is valid."""
        user = User.query.filter_by(activation_token=token).first()
        
        if not user:
            return "Invalid or expired activation link.", 400
        
        user.is_active = True
        user.activation_token = None  
        db.session.commit()
        
        set_message("Account activated successfully! You can now log in.")
        return redirect(url_for('index', module='user_management', submodule='user_list'))
        
    
        
    @app.route('/edit_user/<int:user_id>', methods=['POST'])
    def edit_user(user_id):
        if "admin" not in session.get("roles", []):
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        updates = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "role": request.form.get("role"),
        }
        print(f"🔍 Received Updates: {updates}")
        
        success, message = CRUD.edit_user(user_id, updates)
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":  
            if success:
                return jsonify({"status": "success", "message": message, "redirect": url_for("index", module="user_management", submodule="user_list")})
            
            else:
                return jsonify({"status": "error", "message": message})
        
        
        set_message(message)  
        print(f"🔍 Message set in session: {message}")  
        
        return redirect(url_for('index', module='user_management', submodule='user_list'))
    
    @app.route('/get_user/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        
        # Debugging: Print user data in the Flask console
        print("🟢 Sending User Data:", user.id, user.name, user.email)
        
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.roles[0].name if user.roles else "", 
        })
        
    @app.route('/get_user_table', methods=['GET'])
    def get_user_table():
        users = User.query.all()  # Return full User objects
        return render_template('modules/partials/user_table.html', users=users)
        
    
    
    @app.route('/delete_user/<int:user_id>', methods=['POST'])
    def delete_user(user_id):
        try:
            logging.info(f"Attempting to delete user with ID: {user_id}")
            
            if "admin" not in session.get("roles", []):
                set_message("Unauthorized")
                return jsonify({"success": False, "message": get_message()}), 403
            
            user = User.query.get(user_id)
            if not user:
                set_message("User not found")
                return jsonify({"success": False, "message": get_message()}), 404
            
            success, message = CRUD.delete_record(User, user_id)
            
            if not success:
                set_message(message)
                return jsonify({"success": False, "message": get_message()}), 500
            
            set_message("User deleted successfully!")
            
            return jsonify({"success": True, "message": get_message(), "reload": True}), 200
        
        except Exception as e:
            logging.error(f"Error in delete_user route: {str(e)}")
            set_message("An error occurred while deleting the user")
            return jsonify({"success": False, "message": get_message()}), 500
    
    @app.route("/get_all_roles_permissions", methods=["GET"])
    def get_all_roles_permissions():
        roles = Role.query.all()
        permissions = Permission.query.all()  
        
        roles_data = []
        for role in roles:
            assigned_permissions = {p.id for p in role.permissions}
            role_data = {
                "id": role.id,
                "name": role.name,
                "permissions": [
                    {"id": p.id, "name": p.name, "assigned": p.id in assigned_permissions}
                    for p in permissions
                ],
            }
            roles_data.append(role_data)
        
        return jsonify({"roles": roles_data})
    
    
    @app.route("/modify_permission", methods=["POST"])
    def modify_permission_route():
        data = request.json
        role_id = data.get("role_id")
        permission_id = data.get("permission_id")
        action = data.get("action")
        
        if not role_id or not permission_id or action not in ["add", "remove"]:
            return jsonify({"status": "error", "message": "Invalid input."})
        
        result = CRUD.modify_permission(role_id, permission_id, action)
        return jsonify(result)
    
        
    @app.route('/projects')
    def projects():
        if "user_id" not in session:
            set_message("Login required!")  
            return redirect(url_for("login_page"))
        
        # Load first page & default filter for initial page load
        submodule = request.args.get('submodule', 'ongoing')
        user_roles = session.get("roles", [])  
        message = get_message()  

        user_permissions = session.get("user_permissions", set())
        if not user_permissions:
            roles = Role.query.filter(Role.name.in_(user_roles)).all()
            user_permissions = {perm.name for role in roles for perm in role.permissions}
            session["user_permissions"] = user_permissions
            session.modified = True  

        return render_template(
            'modules/projects.html',
            user_roles=user_roles,
            message=message,
            user_permissions=user_permissions,
            submodule=submodule,
        )
    
        
    
    
    @app.route('/get_project_table', methods=['GET'])
    def get_project_table():
        active_submodule = request.args.get('submodule', 'ongoing')
        page = int(request.args.get('page', 1))
        limit = 5
        
        if active_submodule == "ongoing":
            projects_query = Project.query.filter_by(status="Ongoing")
        elif active_submodule == "finished":
            projects_query = Project.query.filter_by(status="Finished")
        else:
            projects_query = Project.query
        
        pagination = projects_query.paginate(page=page, per_page=limit, error_out=False)
        projects = pagination.items
        total_pages = pagination.pages or 1

        user_permissions = session.get("user_permissions", set())
        
        return render_template(
            'modules/partials/project_table.html',
            projects=projects,
            user_permissions=user_permissions,
            current_page=page,
            total_pages=total_pages
        )
    
    
    
            
        
    
    @app.route('/projects/add', methods=['GET', 'POST'])
    def add_project():
        if request.method == "GET":
            return render_template("modules/add_project.html", message=get_message())
        
        if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
            name = request.form.get('name')
            description = request.form.get('description')
            status = request.form.get('status')
            
            if not all([name, description]):
                return jsonify({"success": False, "message": "Error: All fields are required."})
            
            result = CRUD.add_project(Project, name, description, status)
            
            if result["status"] == "success":
                return jsonify({"success": True, "message": result["message"]})
            else:
                return jsonify({"success": False, "message": result["message"]})
        
        return render_template("modules/add_project.html", message=get_message())
        
    
    @app.route('/projects/view/<int:project_id>', methods=['GET'])
    def view_project(project_id):
        project_data = CRUD.view_project_by_id(Project, project_id)
        
        if not project_data:
            return jsonify({"success": False, "message": "Project not found"}), 404
        
        print(f"Project Data: {project_data}")  
        return jsonify({"success": True, "project": project_data})

    @app.route('/projects/edit/<int:project_id>', methods=['POST'])
    def edit_project(project_id):
        print(f"🔑 Session Permissions: {session.get('user_permissions')}")  

        if "edit" not in session.get("user_permissions", set()):
            print("❌ Access Denied: User does not have 'edit' permission")  
            return jsonify({"success": False, "message": "Unauthorized: You don't have edit permission"}), 403
            
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"status": "error", "message": "Project not found"}), 404
        
        updates = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "status": request.form.get("status"),
        }
        print(f"🔍 Received Updates: {updates}")
        
        success, message = CRUD.edit_project(project_id, updates)
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            if success:
                return jsonify({"status": "success", "message": message, "redirect": url_for("index", module="projects")})
            else:
                return jsonify({"status": "error", "message": message})
        
        set_message(message)  
        print(f"🔍 Message set in session: {message}")  
        
        return redirect(url_for("index", module="projects"))
    
    
    @app.route('/delete_project/<int:project_id>', methods=['POST'])
    def delete_project(project_id):
        try:
            logging.info(f"Attempting to delete project with ID: {project_id}")
            
            if "delete" not in session.get("user_permissions", set()):
                print("❌ Access Denied: User does not have 'delete' permission")  
                return jsonify({"success": False, "message": "Unauthorized: You don't have delete permission"}), 403
            
            project = Project.query.get(project_id)
            if not project:
                set_message("Project not found")
                return jsonify({"success": False, "message": get_message()}), 404
            
            success, message = CRUD.delete_record(Project, project_id)
            
            if not success:
                set_message(message)
                return jsonify({"success": False, "message": get_message()}), 500
            
            set_message("Project deleted successfully!")
            
            return jsonify({"success": True, "message": get_message(), "reload": True}), 200
        
        except Exception as e:
            logging.error(f"Error in delete_project route: {str(e)}")
            set_message("An error occurred while deleting the project")
            return jsonify({"success": False, "message": get_message()}), 500
