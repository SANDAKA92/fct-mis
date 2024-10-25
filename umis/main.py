from flask import request, Blueprint,redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from .models import User, Student, ExamResult

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('login.html')

@main.route('/admin_profile', methods=['GET', 'POST'])
@login_required
def view_admin_profile():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        studentNo = request.form.get('studentNo')
        print(f"StudentNo submitted: {studentNo}")  # Debugging: Ensure the form data is received
        
        # Fetch the student by student number
        #student = User.query.filter_by(reg_no=studentNo).first()
        student = Student.query.filter_by(student_no=studentNo).first()
        if not student:
            flash('Student not found.', 'danger')
           # return render_template('admin_search.html')
        else:
           print('Student with number ', student.student_no, ' found.')

        # Fetch all exam results for the selected student
        exam_results = ExamResult.query.filter_by(studentNo=studentNo)\
         .order_by(ExamResult.acYear, ExamResult.semester).all()
        print(f"Exam results found: {len(exam_results)}") #Debugging
        
        # Group results by academic year and semester
        grouped_results = {}
        for result in exam_results:
            key = (result.acYear, result.semester)
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].append(result)
        
        # Sort the groups by academic year and semester
        sorted_groups = dict(sorted(grouped_results.items()))
        
        return render_template(
            'admin_profile.html',
            student=student,
            grouped_results=sorted_groups
        )
        
    return render_template('admin_search.html')  # Form to input studentNo

@main.route('/profile')
@login_required
def view_student_profile():
    # Fetch the exam results for the current student
    # exam_results = ExamResult.query.filter_by(studentNo=current_user.reg_no).order_by(ExamResult.acYear).all()

    studentNo = current_user.reg_no 
    
    # Fetch the student by student number
    student = Student.query.filter_by(student_no=studentNo).first()
    if not student:
        flash('Student not found.', 'danger')
        return render_template('logout.html')
    else:

       # Fetch all exam results for the selected student
       exam_results = ExamResult.query.filter_by(studentNo=studentNo)\
                       .order_by(ExamResult.acYear, ExamResult.semester).all()
 
       # Group results by academic year and semester
       grouped_results = {}
       for result in exam_results:
           key = (result.acYear, result.semester)
           if key not in grouped_results:
               grouped_results[key] = []
           grouped_results[key].append(result)
       
       # Sort the groups by academic year and semester
       sorted_groups = dict(sorted(grouped_results.items()))
       
       return render_template(
           'profile.html',
           student=student,
           grouped_results=sorted_groups
       )
    
