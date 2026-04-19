from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import sys

# Add honeypot directory to system path to import it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'honeypot')))
from honeypot import log_attack

app = Flask(__name__)
# Secure secret key for flashing messages safely
app.secret_key = 'super_secret_static_key_123'

# Real Database in login_page/instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
# Fake Database mapped to the honeypot folder
fake_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'honeypot', 'fake_database.db'))
app.config['SQLALCHEMY_BINDS'] = {
    'fake_db': f'sqlite:///{fake_db_path}'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model for Authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class RealStudent(db.Model):
    __tablename__ = 'real_student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)

class FakeStudent(db.Model):
    __bind_key__ = 'fake_db'
    __tablename__ = 'fake_student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)

def get_student_model():
    if session.get('is_hacker'):
        return FakeStudent
    return RealStudent

# Initialize the database correctly with app context
with app.app_context():
    db.create_all()

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = user.username
            session['is_hacker'] = False
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            log_attack(request.remote_addr, username, password)
            session['logged_in'] = True
            session['username'] = username if username else 'Guest'
            session['is_hacker'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    StudentModel = get_student_model()
    students = StudentModel.query.order_by(StudentModel.enrollment_date.desc()).all()
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        
        StudentModel = get_student_model()
        # Check for existing email to avoid integrity errors
        existing_student = StudentModel.query.filter_by(email=email).first()
        if existing_student:
            flash(f"Error: A student with email {email} already exists.", "error")
            return render_template('add_edit.html', action="Add", student=None)
            
        new_student = StudentModel(name=name, email=email, course=course)
        try:
            db.session.add(new_student)
            db.session.commit()
            flash("Student successfully added!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            
    return render_template('add_edit.html', action="Add", student=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    StudentModel = get_student_model()
    student = StudentModel.query.get_or_404(id)
    
    if request.method == 'POST':
        student.name = request.form['name']
        
        # Validate email change
        new_email = request.form['email']
        if new_email != student.email:
            existing_student = StudentModel.query.filter_by(email=new_email).first()
            if existing_student:
                flash(f"Error: Email {new_email} is already taken.", "error")
                return render_template('add_edit.html', action="Edit", student=student)
                
        student.email = new_email
        student.course = request.form['course']
        
        try:
            db.session.commit()
            flash("Student details updated successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            
    return render_template('add_edit.html', action="Edit", student=student)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    StudentModel = get_student_model()
    student = StudentModel.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        flash(f"Student {student.name} was removed.", "success")
    except Exception as e:
        flash(f"An error occurred during deletion: {str(e)}", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Start the application on port 5000
    app.run(debug=True, port=5000)
