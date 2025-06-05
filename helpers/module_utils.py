from models import db, User, Role, Permission, UserRoles, role_permissions, Project, Module, Submodule

# Function to get modules and submodules associated with the user based on their roles
def get_user_modules_and_submodules(user_id):
    modules = set()
    submodules = set()
    
    # Ensure user_id is valid and fetch the User object
    user = User.query.get(user_id)  # Retrieve the full User object from the database
    if user is None:
        print("Error: User not found in the database.")
        return modules, submodules
    
    # Now proceed with roles as the user object is correctly retrieved
    for role in user.roles:
        # Add all modules related to the role
        for module in role.modules:
            modules.add(module)
        
        # Add all submodules related to the role
        for submodule in role.submodules:
            submodules.add(submodule)
    
    print(f"Modules: {[module.name for module in modules]}")
    print(f"Submodules: {[submodule.name for submodule in submodules]}")
    
    return modules, submodules


# Function to get accessible modules and submodules based on user roles
def get_accessible_modules_with_submodules(user):
    # Get modules and submodules for the user's roles
    modules, submodules = get_user_modules_and_submodules(user)

    # Add dashboard manually if it exists and is public
    dashboard_module = Module.query.filter_by(name='dashboard').first()
    if dashboard_module and dashboard_module not in modules:
        modules.add(dashboard_module)

    # Sort modules by sequence (ensure each module has a 'sequence' attribute)
    module_list = sorted(modules, key=lambda m: m.sequence if hasattr(m, 'sequence') else 0)

    print(f"Sorted Modules: {[module.name for module in module_list]}")

    result = []
    for module in module_list:
        print(f"Checking submodules for module: {module.name}")
        
        # Find submodules for this module that are accessible by the roles
        submodules_query = Submodule.query.filter(
            Submodule.module_id == module.id,
            Submodule.id.in_([sm.id for sm in submodules])  # Use IDs of accessible submodules
        ).order_by(Submodule.sequence).all()

        print(f"Found submodules for {module.name}: {[sm.name for sm in submodules_query]}")

        # Prepare submodule data
        submodules_data = [
            {
                "id": sm.id,
                "name": sm.name,
                "display_name": sm.display_name,
                "icon": sm.icon,
                "url": sm.url
            } for sm in submodules_query
        ]

        # Append module and its submodules
        result.append({
            "id": module.id,
            "name": module.name,
            "display_name": module.display_name,
            "icon": module.icon,
            "url": module.url,
            "is_parent": bool(submodules_data),
            "submodules": submodules_data
        })

    print(f"Final Result: {result}")

    return result
