from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import with_appcontext
from sqlalchemy.exc import SQLAlchemyError
from .models import User, Student, Staff, UserRole, db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Fetch user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('User not found.')
            return redirect(url_for('auth.login'))

        if not user.password:
            flash('No password set. Please sign up to set a password.')
            return redirect(url_for('auth.signup'))

        if check_password_hash(user.password, password):
            login_user(user)

            # Redirect based on role
            if user.role == UserRole.ADMIN:
                return redirect(url_for('main.view_admin_profile'))
            elif user.role == UserRole.STUDENT:
                return redirect(url_for('main.view_student_profile'))
            elif user.role == UserRole.STAFF:
                return redirect(url_for('main.view_staff_profile'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        student_id = request.form.get('student_id')
        nic = request.form.get('nic')
        phone_no = request.form.get('phone_no')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(email=email, reg_no=student_id).first()

        if not user:
            flash(f'No matching record for student_id: {student_id} and email: {email}.')
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
    logout_user()
    message = f"Thank you for using the FCT Examination Results Information System, {current_user.reg_no}." if not current_user.is_anonymous else "You have successfully logged out."
    return render_template('logout.html', message=message)

@auth.cli.command('create-admin')
@with_appcontext
def create_admin():
    reg_no = input("Enter admin registration number: ")
    name = input("Enter admin name: ")
    email = input("Enter admin email: ")
    phone_no = input("Enter admin phone number: ")
    nic = input("Enter NIC: ")
    password = input("Enter password: ")

    hashed_password = generate_password_hash(password)

    if User.query.filter((User.email == email) | (User.reg_no == reg_no)).first():
        print("Admin with this email or registration number already exists!")
        return

    admin = User(
        reg_no=reg_no,
        email=email,
        password=hashed_password,
        role=UserRole.ADMIN
    )

    staff = Staff(
        salary_no=reg_no,
        nic=nic,
        email=email,
        phone_no=phone_no,
        name=name
    )

    db.session.add(admin)
    db.session.add(staff)
    db.session.commit()
    print(f"Admin account for {name} created successfully!")

@auth.cli.command('create-student')
@with_appcontext
def create_student():
    reg_no = input("Enter student registration number: ")
    email = input("Enter student email: ")
    nic = input("Enter NIC: ")
    phone_no = input("Enter phone number: ")
    password = input("Enter password: ")

    student = Student.query.filter_by(id=reg_no, email=email).first()

    if not student:
        print("No matching student record found.")
        return

    if User.query.filter((User.email == email) | (User.reg_no == reg_no)).first():
        print("User with this email or registration number already exists!")
        return

    hashed_password = generate_password_hash(password)

    user = User(
        reg_no=reg_no,
        email=email,
        password=hashed_password,
        role=UserRole.STUDENT
    )

    db.session.add(user)
    db.session.commit()
    print(f"Student account for {reg_no} created successfully!")
