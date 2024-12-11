from flask import request, Blueprint, redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from .models import User, Student, StudentCourseGrade, UserRole

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('login.html')

@main.route('/admin_profile', methods=['GET', 'POST'])
@login_required
def view_admin_profile():
    if current_user.role != UserRole.ADMIN:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        
        # Fetch the student by student ID
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            flash('Student not found.', 'danger')
            return render_template('admin_search.html')

        # Fetch all exam results for the selected student
        exam_results = StudentCourseGrade.query.filter_by(student_id=student_id).all()

        # Group results by academic year and semester
        grouped_results = {}
        for result in exam_results:
            key = (result.ac_year, result.semester)
            grouped_results.setdefault(key, []).append(result)

        # Sort the groups by academic year and semester
        sorted_groups = dict(sorted(grouped_results.items()))

        return render_template(
            'admin_profile.html',
            student=student,
            grouped_results=sorted_groups
        )

    return render_template('admin_search.html')

@main.route('/profile')
@login_required
def view_student_profile():
    if current_user.role != UserRole.STUDENT:
        flash('Access denied. Student privileges required.', 'danger')
        return redirect(url_for('main.index'))

    # Fetch the student by user ID
    student = Student.query.filter_by(id=current_user.reg_no).first()
    if not student:
        flash('Student record not found.', 'danger')
        return redirect(url_for('auth.logout'))

    # Fetch all exam results for the logged-in student
    exam_results = ExamResult.query.filter_by(student_id=student.id).order_by(ExamResult.ac_year, ExamResult.semester).all()

    # Group results by academic year and semester
    grouped_results = {}
    for result in exam_results:
        key = (result.ac_year, result.semester)
        grouped_results.setdefault(key, []).append(result)

    # Sort the groups by academic year and semester
    sorted_groups = dict(sorted(grouped_results.items()))

    return render_template(
        'profile.html',
        student=student,
        grouped_results=sorted_groups
    )
