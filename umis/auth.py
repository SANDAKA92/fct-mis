from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import with_appcontext
from .models import User, Student, Staff,db
import bcrypt
from sqlalchemy import text

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('User not found')
            return redirect(url_for('auth.login'))
        
        if not user.password:
            flash('No password set. Please sign up to set a password.')
            return redirect(url_for('auth.signup'))
        
        if check_password_hash(user.password, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('main.view_admin_profile'))
            elif user.user_type == 'student':
                return redirect(url_for('main.view_student_profile'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        student_no = request.form.get('student_no')
        nic = request.form.get('nic')
        phone_no = request.form.get('phone_no')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(email=email, reg_no=student_no).first()

        if not user:
            message = 'No matching record for student_no: ' + student_no + ' and email: ' + email
            flash(message)
            return redirect(url_for('auth.signup'))
        
        if user.password:
            flash('Password already set. Please log in.')
            return redirect(url_for('auth.login'))
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('auth.signup'))
        
        user.nic = nic
        user.phone_no = phone_no
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()
        
        flash('Password set successfully. You can now log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth.route('/logout')
def logout():
    # Log out the user
    logout_user()

    # Check if current_user is anonymous (no logged-in user)
    if current_user.is_anonymous:
        return render_template('logout.html', message="You have successfully logged out.")

    # Otherwise, display a personalized logout message
    return render_template('logout.html', message=f"Thank you for using the FCT Examination Results Information System, {current_user.reg_no}.")


@auth.cli.command('create-admin')
@with_appcontext  # Ensures the command runs within the application context
def create_admin():
    """Create an admin user."""
    # Collecting necessary details for the admin
    reg_no = input("Enter admin registration number: ")
    name = input("Enter admin name: ")
    email = input("Enter admin email: ")
    phone_no = input("Enter admin phone number: ")
    status = input("Staff status (PL|VL|TL|NS): ")
    nic = input("Enter NIC: ")
    password = input("Enter password: ")
    
    #hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_password = generate_password_hash(password)

    # Check if an admin with the given email, registration number, or NIC already exists
    if User.query.filter((User.email == email) | (User.reg_no == reg_no) ).first():
        print("Admin with this email, registration number, or NIC already exists!")
        return

    # Create the admin account
    admin = User(
        reg_no=reg_no,
        email=email,
        password=hashed_password,  # Store the hashed password as a string
        is_admin=True,  # Set as admin
        user_type='staff'  # Example: Set user_type as 'staff' for all academic/non-academic/academic-support staff 
    )

    staff = Staff(
            salary_no=reg_no,
            nic = nic,
            email = email,
            phone_no = phone_no,
            name = name,
            utype = status
    )

    # Add the new admin user to the database
    db.session.add(admin)
    db.session.add(staff)
    db.session.commit()

    print(f"Admin account for {name} created successfully!")


@auth.cli.command('create-student')
@with_appcontext
def create_student():
    """Create a student user after validating against Student table."""
    # Collecting necessary details
    reg_no = input("Enter student registration number: ")
    email = input("Enter student email: ")
    phone_no = input("Enter phone number: ")
    nic = input("Enter NIC: ")
    password = input("Enter password: ")

    # First, check if the student exists in the Student table with matching email and reg_no
    existing_student = Student.query.filter_by(
        student_no=reg_no,
        email=email
    ).first()

    if not existing_student:
        print("Error: No matching student record found in Student table. Please ensure the student is registered in the system first.")
        return

    # Check if user account already exists
    hashed_password = generate_password_hash(password)
    
    if User.query.filter(
        (User.email == email) | 
        (User.reg_no == reg_no)
    ).first():
        print("Error: User account with this email or registration number already exists!")
        #return

    try:
        # Update the existing student record with the user_id
        existing_student.password = hashed_password
        existing_student.phone_no = phone_no  # Update phone number
        existing_student.nic = nic  # Update NIC
        existing_student.is_admin = False  # Update NIC
        existing_student.user_type = 'student'  # Update NIC

        db.session.commit()
        print(f"Student account for {reg_no} updated successfully!")

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error creating student account: {str(e)}")
        return

    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error occurred: {str(e)}")
        return

