from flask import request, Blueprint,redirect, url_for, render_template, flash
from flask_login import login_required, current_user
from .models import User, Student, ExamResult, calculate_gpa

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
    print(f"StudentNo submitted: {studentNo}")  # Debugging: Ensure the form data is received
    
    # Fetch the student by student number
    student = Student.query.filter_by(student_no=studentNo).first()
    if not student:
        flash('Student not found.', 'danger')
        return render_template('logout.html')
    else:
       print('Student with number ', student.student_no, ' found.')

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
    
'''

@main.route('/admin_profile', methods=['GET', 'POST'])
@login_required
def view_admin_profile():
    if request.method == 'POST':
        studentNo = request.form.get('studentNo')
        print(f"StudentNo submitted: {studentNo}")  # Debugging: Ensure the form data is received

        # Fetch the student by student number
        student = User.query.filter_by(reg_no=studentNo).first()

        if not student:
            flash('Student not found.', 'danger')
#            return redirect(url_for('main.view_admin_profile'))

        # Fetch all exam results for the selected student
        exam_results = ExamResult.query.filter_by(studentNo=studentNo).order_by(ExamResult.acYear).all()
        print(f"Exam results found: {len(exam_results)}") #Debugging

        return render_template('admin_profile.html', student=student, exam_results=exam_results)
    return render_template('admin_search.html')  # Form to input studentNo
@main.route('/admin_profile', methods=['GET', 'POST'])
@login_required
def view_admin_profile():

    student = None
    grades = []
    cumulative_gpa = credits_below_c = credits_greater_than_c = total_e_credits = None

    if request.method == 'POST':
        student_no = request.form.get('student_no')
        student = User.query.filter_by(reg_no=student_no).first()

        if student:
            # Get the student's grades
            grades = StudentGrade.query.filter_by(studentNo=student_no).order_by(StudentGrade.level, StudentGrade.semester).all()
 
            # Calculate GPA
            cumulative_gpa, credits_below_c, credits_greater_than_c, total_e_credits = calculate_gpa(student_no)
        else:
            flash('No student found with the provided student number. Please check the number and try again.', 'warning')

 
    return render_template('admin_profile.html', student=student, grades=grades,
                           cumulative_gpa=cumulative_gpa, credits_below_c=credits_below_c,
                           credits_greater_than_c=credits_greater_than_c, total_e_credits=total_e_credits)

@main.route('/profile')
@login_required
def view_student_profile():
    # Get the student's grades
    grades = StudentGrade.query.filter_by(studentNo=current_user.studentNo).order_by(StudentGrade.level, StudentGrade.semester).all()

    # Calculate GPA
    cumulative_gpa, grades_below_d, grades_greater_than_e, total_e_grades = calculate_gpa(current_user.studentNo)

    return render_template('profile.html', grades=grades, cumulative_gpa=cumulative_gpa,
                           grades_below_d=grades_below_d, grades_greater_than_e=grades_greater_than_e,
                           total_e_grades=total_e_grades)
'''

