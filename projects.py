from app import app, db  # Import the Flask app instance
from models import Project  # Import the Project model

# Sample project data
projects = [
    {"name": "Website Redesign", "description": "Revamp the company's main website."},
    {"name": "Mobile App Development", "description": "Create a cross-platform mobile application."},
    {"name": "Marketing Campaign", "description": "Launch a new digital marketing strategy."},
    {"name": "CRM System Upgrade", "description": "Upgrade the existing CRM software."},
    {"name": "Employee Training Program", "description": "Develop a new training curriculum for employees."}
]

# Use the application context
with app.app_context():
    for project_data in projects:
        project = Project(**project_data)
        db.session.add(project)

    db.session.commit()
    print("Project table populated successfully!")
