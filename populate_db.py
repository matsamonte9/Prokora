from app import app, db
from models import Module, Submodule, Role, submodule_roles  # Ensure submodule_roles is accessible
from sqlalchemy import text  # Import the text function

def update_submodule_roles():
    with app.app_context():
        # List of submodule data to move from Module table to Submodule table, including roles
        submodules_data = [
            {'name': 'user_list', 'display_name': 'User List', 'icon': 'list_alt', 'url': '/load_module/user_list', 'sequence': 1, 'parent_module_name': 'user_management', 'roles': ['admin']},
            {'name': 'user_profile', 'display_name': 'User Profile', 'icon': 'person', 'url': '/load_module/user_profile', 'sequence': 2, 'parent_module_name': 'user_management', 'roles': ['admin']},
            {'name': 'ongoing', 'display_name': 'Ongoing', 'icon': 'event_repeat', 'url': '/load_module/ongoing', 'sequence': 1, 'parent_module_name': 'projects', 'roles': ['admin', 'project']},
            {'name': 'finished', 'display_name': 'Finished', 'icon': 'task_alt', 'url': '/load_module/finished', 'sequence': 2, 'parent_module_name': 'projects', 'roles': ['admin', 'project']}
        ]

        for submodule_data in submodules_data:
            # Find the parent module (user_management or projects)
            parent_module = Module.query.filter_by(name=submodule_data['parent_module_name']).first()

            if parent_module:
                try:
                    # Check if the submodule already exists in the submodule table
                    existing_submodule = Submodule.query.filter_by(name=submodule_data['name']).first()
                    if not existing_submodule:
                        # If submodule doesn't exist, create it
                        new_submodule = Submodule(
                            name=submodule_data['name'],
                            display_name=submodule_data['display_name'],
                            icon=submodule_data['icon'],
                            url=submodule_data['url'],
                            sequence=submodule_data['sequence'],
                            module_id=parent_module.id  # Link the submodule to the parent module
                        )

                        db.session.add(new_submodule)
                        db.session.commit()
                        print(f"Added submodule {submodule_data['name']} under parent module {parent_module.name}")
                    else:
                        # If submodule exists, use the existing one
                        new_submodule = existing_submodule
                        print(f"Submodule {submodule_data['name']} already exists, using existing submodule.")

                    # Now, associate the submodule with the specified roles
                    for role_name in submodule_data['roles']:
                        role = Role.query.filter_by(name=role_name).first()  # Find the role by name
                        if role:
                            # Check if the combination of submodule_id and role_id already exists in submodule_roles table
                            existing_entry = db.session.query(db.exists().where(
                                (submodule_roles.c.submodule_id == new_submodule.id) & (submodule_roles.c.role_id == role.id)
                            )).scalar()

                            if not existing_entry:  # If no such entry exists
                                # Insert a record into submodule_roles table using text()
                                db.session.execute(
                                    text('INSERT INTO submodule_roles (submodule_id, role_id) VALUES (:submodule_id, :role_id)'),
                                    {'submodule_id': new_submodule.id, 'role_id': role.id}
                                )
                                print(f"Assigned role {role_name} to submodule {submodule_data['name']}")
                            else:
                                print(f"Role {role_name} already assigned to submodule {submodule_data['name']}, skipping.")
                        else:
                            print(f"Role {role_name} not found for submodule {submodule_data['name']}")
                        
                except Exception as e:
                    print(f"Error processing submodule {submodule_data['name']} under parent module {parent_module.name}: {e}")
            else:
                print(f"Parent module {submodule_data['parent_module_name']} not found.")

        try:
            db.session.commit()
            print("Submodule roles have been updated successfully.")
        except Exception as e:
            print(f"Error committing submodule roles: {e}")
            db.session.rollback()

if __name__ == "__main__":
    update_submodule_roles()
