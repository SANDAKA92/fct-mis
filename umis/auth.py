from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import with_appcontext
from .models import User, Student, Staff,db
import bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user: 
        #and check_password_hash(user.password, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('main.view_admin_profile'))
            elif user.user_type == 'student':
                return redirect(url_for('main.view_student_profile'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

# Route for displaying the signup form
@auth.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

# Route for handling signup form submission
@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    nic = request.form.get('nic')
    reg_no = request.form.get('reg_No')
    password = request.form.get('password')
    #hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_password = generate_password_hash(password)

    # Validate student number
    if not StudentGrade.query.filter_by(studentNo=student_no).first():
        flash('Invalid Student Number')
        return redirect(url_for('auth.signup'))

    # Validate email domain
    if not email.endswith('@stu.kln.ac.lk'):
        flash('Email must be a university email address (@stu.kln.ac.lk)')
        return redirect(url_for('auth.signup'))

    # Check if user exists
    if User.query.filter_by(email=email).first():
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # Create new user
    new_user = User(email=email, nic=nic, reg_no=reg_no, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

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
        '''
        # Create the user account
        new_user = User(
            reg_no=reg_no,
            email=email,
            password=hashed_password,
            is_admin=False,
            user_type='student'
        )
        db.session.add(new_user)
        db.session.flush()  # This assigns the ID to new_user before commit
        '''
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
