import random
from app import app, db, User, RealStudent, FakeStudent
from werkzeug.security import generate_password_hash

names = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Prince", "Evan Davis", "Fiona Gallagher", "George Martin", "Hannah Abbott"]
courses = ["Computer Science", "Mathematics", "Physics", "Chemistry", "Biology", "History", "Literature"]

with app.app_context():
    # Recreate the database schema for ALL binds
    db.drop_all()
    db.create_all()

    # Add a default admin user for testing
    admin_user = User(username='admin', password=generate_password_hash('password123'))
    db.session.add(admin_user)
    
    # Add the user you were specifically trying to log in with
    user_test = User(username='33@gmail.com', password=generate_password_hash('password123'))
    db.session.add(user_test)

    # Add real students (Real Application Data)
    for i in range(1, 11):
        name = random.choice(names) + f" (Real {i})"
        email = f"real_student{i}@example.com"
        course = random.choice(courses)
        student = RealStudent(name=name, email=email, course=course)
        db.session.add(student)
        
    # Add fake students (Honeypot Data)
    for i in range(1, 21):
        name = random.choice(names) + f" (Fake {i})"
        email = f"fake_student{i}@example.com"
        course = random.choice(courses)
        student = FakeStudent(name=name, email=email, course=course)
        db.session.add(student)
    
    db.session.commit()
    print("Successfully created real database AND fake database in the honeypot folder!")
