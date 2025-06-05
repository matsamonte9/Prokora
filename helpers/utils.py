from functools import wraps
from flask import session, redirect, url_for, request, abort

def permission_required(required_roles=None, required_permissions=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login_page"))
            
            user_roles = session.get("roles", [])
            user_permissions = session.get("user_permissions", [])

            # Check roles
            if required_roles:
                if not any(role in user_roles for role in required_roles):
                    return abort(403)  # Forbidden

            # Check permissions
            if required_permissions:
                if not any(perm in user_permissions for perm in required_permissions):
                    return abort(403)  # Forbidden

            return f(*args, **kwargs)
        return wrapper
    return decorator
