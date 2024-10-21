from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(20), unique=True) # students - index no | staff - salary number
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    user_type = db.Column(db.String(10)) #student |staff

    # Add relationship to Student model
    student = db.relationship('Student', backref='user', uselist=False)
    staff = db.relationship('Staff', backref='user', uselist=False)



class Student(db.Model):
    __tablename__ = 'student'
    student_no = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    nic = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, unique=True)
    phone_no = db.Column(db.String(12), unique=True)
    name = db.Column(db.Text)
    entered_acYear = db.Column(db.String(12))
    reg_status = db.Column(db.String(2)) #RN- Registerd Normal|UR - Unregistered|Sus - Suspended|Grd - Graduated
    
    # Relationship with the exam results
    exam_results = db.relationship('ExamResult', back_populates='student')

class Staff(db.Model):
    __tablename__ = 'staff'
    
    salary_no = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    nic = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, unique=True)
    phone_no = db.Column(db.String(12), unique=True)
    name = db.Column(db.Text)
    utype = db.Column(db.String(2)) #PL - Permanant Lecturer| TL - Temporary Lecturer| VL - Visiting Lecturer |EU - Exam Unit|RG - Registrar

class Exams(db.Model):
    __tablename__ = 'exams'
    
    examId = db.Column(db.Integer, primary_key=True)
    degreeCode = db.Column(db.String(20), primary_key=True)
    acYear = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.Integer,primary_key=True)
    examStatusId = db.Column(db.Integer, primary_key=True)
    courseCode = db.Column(db.String(20), primary_key=True)
    deptCode = db.Column(db.String(20))
    examiner_1_reg_no = db.Column(db.String(20),db.ForeignKey('staff.salary_no'))
    examiner_2_reg_no = db.Column(db.String(20),db.ForeignKey('staff.salary_no'))
    examiner_3_reg_no = db.Column(db.String(20),db.ForeignKey('staff.salary_no'))
    dean_reg_no =  db.Column(db.String(20),db.ForeignKey('staff.salary_no'))
    hod_reg_no = db.Column(db.String(20),db.ForeignKey('staff.salary_no'))
    results_status = db.Column(db.String(20)) 

class ExamResult(db.Model):
    #Table for holding data of legacy MIS developed by Mr. Samantha
    __tablename__ = 'exam_results'
    
    examId = db.Column(db.Integer, primary_key=True)
    degreeCode = db.Column(db.String(20), primary_key=True)
    acYear = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.Integer,primary_key=True)
    examStatusId = db.Column(db.Integer, primary_key=True)
    attempt = db.Column(db.Integer, primary_key=True)
    studentNo = db.Column(db.String(20), db.ForeignKey('student.student_no'),primary_key=True)  # Foreign key to Student table
    courseCode = db.Column(db.String(20), primary_key=True)
    ca_marks = db.Column(db.Float)  # Continuous assessment marks
    th_marks = db.Column(db.Float)  # Theory marks
    pr_marks = db.Column(db.Float)  # Practical marks
    total_marks = db.Column(db.Float)  # Total marks
    ca_grade = db.Column(db.String(5))  # Continuous assessment grade
    th_grade = db.Column(db.String(5))  # Theory grade
    pr_grade = db.Column(db.String(5))  # Practical grade
    grade = db.Column(db.String(5))  # Final exam grade
    grd_comments = db.Column(db.Text)  # Comments for the student, especially for 'Inc'
    
    # Relationship with the student (user)
    student = db.relationship('Student', back_populates='exam_results')

class ExamRegistration(db.Model):
    degreeCode = db.Column(db.String(10), primary_key=True)
    acYear = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.Integer, primary_key=True) # 1 - First Semester | 2 - Second Semester
    examStatusId = db.Column(db.Integer, primary_key=True) #1-Normal | 2-Repeat | 3 - Resit  
    regStatus = db.Column(db.String(2)) #P-proper | R-repeat | RF - repeat as first time
    rpt_component = db.Column(db.String(4)) # ca | esth | espr
    studentNo = db.Column(db.String(20), primary_key=True)
    courseCode = db.Column(db.String(10), primary_key=True)
    attempt = db.Column(db.Integer)

class StudentGrade(db.Model):
    degreeCode = db.Column(db.String(10), primary_key=True)
    acYear = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.Integer, primary_key=True) # 1 - First Semester | 2 - Second Semester
    examStatusId = db.Column(db.Integer, primary_key=True) #1-Normal | 2-Repeat | 3 - Resit  
    studentNo = db.Column(db.String(20), primary_key=True)
    courseCode = db.Column(db.String(10), primary_key=True)
    attendance = db.Column(db.String(2))
    ca_grade = db.Column(db.String(2))
    ca_marks = db.Column(db.Integer)
    th_grade = db.Column(db.String(2))
    th_marks = db.Column(db.Integer)
    pr_grade = db.Column(db.String(2))
    pr_marks = db.Column(db.Integer)
    final_grade = db.Column(db.String(2))
    final_marks = db.Column(db.Integer)
    rpt_comment = db.Column(db.String(255))

class DegreeCourseReq(db.Model):
    degreeCode = db.Column(db.String(10), primary_key=True)
    courseCode = db.Column(db.String(10), primary_key=True)
    subjCode = db.Column(db.String(10))
    level = db.Column(db.Integer)
    courseTitle = db.Column(db.String(255))
    creditHrs = db.Column(db.Integer)
    compulsory = db.Column(db.Integer)
    gpaCredits = db.Column(db.Integer)

class DegreeData(db.Model):
    degreeCode = db.Column(db.String(10), primary_key=True)
    acYear = db.Column(db.Integer, primary_key=True)
    facCode = db.Column(db.String(10), primary_key=True)
    deptCode = db.Column(db.String(10), primary_key=True)
    coordRegNo = db.Column(db.String(20), unique=True)
    headRegNo = db.Column(db.String(20), unique=True)
    deanRegNo = db.Column(db.String(20), unique=True)

class GradeLetterInfo(db.Model):
    degreeCode = db.Column(db.String(10), primary_key=True)
    gradeLetter = db.Column(db.String(2), primary_key=True)
    gpv = db.Column(db.Float)


def calculate_gpa(student_no):
    grades = StudentGrade.query.filter_by(studentNo=student_no).all()
    total_gpv = 0
    total_credits = 0
    credits_below_c = 0
    credits_greater_than_c = 0
    total_e_credits = 0

    for grade in grades:
        grade_info = GradeLetterInfo.query.filter_by(gradeLetter=grade.grade).first()
        course_info = DegreeCourseReq.query.filter_by(courseCode=grade.courseCode, degreeCode=grade.degreeCode).first()

        if grade_info and course_info:
            total_gpv += grade_info.gpv * course_info.gpaCredits
            total_credits += course_info.gpaCredits

            if grade.grade in ['C-','D+','D']:
                credits_below_c += course_info.gpaCredits
            if grade.grade in ['C+','B-','B','B+','A-','A','A+']:
                credits_greater_than_c += course_info.gpaCredits
            if grade.grade in ['E', 'Inc', 'Ab', 'Rpt']:
                total_e_credits += course_info.gpaCredits

    if total_credits == 0:
        return 0.0, credits_below_c, credits_greater_than_c, total_e_credits

    return total_gpv / total_credits, credits_below_c, credits_greater_than_c, total_e_credits
