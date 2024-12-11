import os
from enum import Enum
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from . import db  # Assuming you're using a db instance from a Flask SQLAlchemy extension


class UserRole(Enum):
    ADMIN = "admin"
    HOD = "hod"
    DEAN = "dean"
    EXAM_UNIT = "exam_unit"
    REGISTRAR = "registrar"
    STAFF = "staff"
    STUDENT = "student"

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(20), unique=True)  # students - index no | staff - salary number
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    
    # Role field instead of multiple booleans
    role = db.Column(SQLAEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    user_type = db.Column(db.String(10), nullable=False)  # "student" or "staff"

    # Relationships to Student and Staff models
    student = db.relationship('Student', backref='user', uselist=False)
    staff = db.relationship('Staff', backref='user', uselist=False)

    def has_role(self, *roles):
        """Check if the user has one of the specified roles."""
        return self.role in roles

    def is_admin(self):
        """Check if the user is an admin."""
        return self.role == UserRole.ADMIN

    def is_hod(self):
        """Check if the user is a head of department."""
        return self.role == UserRole.HOD

    def is_dean(self):
        """Check if the user is a dean."""
        return self.role == UserRole.DEAN

    def is_exam_unit(self):
        """Check if the user is part of the exam unit."""
        return self.role == UserRole.EXAM_UNIT

    def is_registrar(self):
        """Check if the user is the registrar."""
        return self.role == UserRole.REGISTRAR

class Student(db.Model):
    __tablename__ = 'student'
    
    student_no = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    nic = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, unique=True)
    phone_no = db.Column(db.String(12), unique=True)
    name = db.Column(db.Text)
    entered_acYear = db.Column(db.String(12))
    cGPA = db.Column(db.Float)
    reg_status = db.Column(db.String(2))  # RN - Registered Normal | UR - Unregistered | Sus - Suspended | Grd - Graduated

    # Relationship with Registration
    registrations = db.relationship('Registration', back_populates='student')

class Staff(db.Model):
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True)
    salary_no = db.Column(db.String(20), unique=True, nullable=True)  # Nullable for staff without salary number
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    nic = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, unique=True)
    phone_no = db.Column(db.String(12), unique=True)
    name = db.Column(db.Text)
    utype = db.Column(db.String(2))  # PL - Permanent Lecturer | TL - Temporary Lecturer | VL - Visiting Lecturer | EU - Exam Unit | RG - Registrar

    # Relationships as examiners
    first_exams = relationship("Exam", foreign_keys='Exam.first_examiner_id', back_populates="first_examiner")
    second_exams = relationship("Exam", foreign_keys='Exam.second_examiner_id', back_populates="second_examiner")

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    degree_code = db.Column(db.String(10), ForeignKey('degrees.code'), nullable=False)
    dept_code = db.Column(db.String(10), ForeignKey('departments.code'), nullable=False)

    # One-to-one relationship with Exam
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), unique=True, nullable=True)
    exam = relationship("Exam", back_populates="course", uselist=False)
    
    ca_weight = db.Column(db.Float, nullable=False)
    fe_th_weight = db.Column(db.Float, nullable=False)
    fe_pr_weight = db.Column(db.Float, nullable=True)

    allocated_lecture_hours = db.Column(db.Integer, nullable=False)
    allocated_practical_hours = db.Column(db.Integer, nullable=True)
    allocated_tutorial_hours = db.Column(db.Integer, nullable=True)
    conducted_lecture_hours = db.Column(db.Integer, nullable=False)
    conducted_practical_hours = db.Column(db.Integer, nullable=True)
    conducted_tutorial_hours = db.Column(db.Integer, nullable=True)

    # Relationships
    degree = relationship("Degree", back_populates="courses")
    department = relationship("Department", back_populates="courses")
    registrations = relationship("Registration", back_populates="course")

class Exam(db.Model):
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    ac_year = db.Column(db.String(10), nullable=False)
    level = db.Column(db.String(10), nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    exam_status_id = db.Column(db.String(10), nullable=False)
    course_code = db.Column(db.String(10), ForeignKey('courses.code'), nullable=False)
    dept_code = db.Column(db.String(10), ForeignKey('departments.code'), nullable=False)

    # Foreign key for one-to-one relationship with Course
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), unique=True, nullable=True)
    course = relationship("Course", back_populates="exam", uselist=False)

    first_examiner_id = db.Column(db.Integer, ForeignKey('staff.id'), nullable=False)
    second_examiner_id = db.Column(db.Integer, ForeignKey('staff.id'), nullable=False)

    # Paths to PDF files for each stage in the exam paper setting
    draft_pdf_path = db.Column(db.String(200))             # Initial draft PDF
    review_pdf_path = db.Column(db.String(200))            # Review comments PDF
    modified_pdf_path = db.Column(db.String(200))          # Modified paper PDF
    approved_pdf_path = db.Column(db.String(200))          # Final approved version PDF

    # Dates associated with paper setting stages
    draft_submission_date = db.Column(DateTime)
    review_submission_date = db.Column(DateTime)
    modification_submission_date = db.Column(DateTime)
    head_approval_date = db.Column(DateTime)
    ready_for_print_date = db.Column(DateTime)

    # Dates for marking and approval process
    examiner1_marking_date = db.Column(DateTime)
    examiner2_review_date = db.Column(DateTime)
    hod_final_approval_date = db.Column(DateTime)
    exam_board_approval_date = db.Column(DateTime)
    dean_approval_date = db.Column(DateTime)
    registrar_release_date = db.Column(DateTime)

    # Relationships
    course = relationship("Course", back_populates="exams")
    registrations = relationship("Registration", back_populates="exam")

    # Relationships for examiners
    first_examiner = relationship("Staff", foreign_keys=[first_examiner_id], back_populates="first_exams")
    second_examiner = relationship("Staff", foreign_keys=[second_examiner_id], back_populates="second_exams")

    # Unique constraint to prevent duplicate exams for the same course in the same semester and academic year
    __table_args__ = (
        UniqueConstraint('course_code', 'ac_year', 'level', 'semester', 'exam_status_id', name='unique_exam'),
    )

    def save_document(self, file, stage):
        """Save uploaded PDF for the specified stage and update path."""
        filename = f"{self.id}_{stage}.pdf"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Save file to designated folder
        file.save(file_path)

        # Update database path field and date based on stage
        if stage == 'draft':
            self.draft_pdf_path = file_path
            self.draft_submission_date = datetime.utcnow()
        elif stage == 'review':
            self.review_pdf_path = file_path
            self.review_submission_date = datetime.utcnow()
        elif stage == 'modified':
            self.modified_pdf_path = file_path
            self.modification_submission_date = datetime.utcnow()
        elif stage == 'approved':
            self.approved_pdf_path = file_path
            self.head_approval_date = datetime.utcnow()
            self.ready_for_print_date = datetime.utcnow()
        
        db.session.commit()

class Registration(db.Model):
    __tablename__ = 'registration'
    
    id = db.Column(db.Integer, primary_key=True)
    student_no = db.Column(db.String(20), db.ForeignKey('student.student_no'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    registration_type = db.Column(db.String(10))  # "first-time" or "repeat"
    attempt_count = db.Column(db.Integer, default=1)

    # Marks and grades by examiner 1 and examiner 2
    ca_marks_examiner1 = db.Column(db.Float)
    fe_th_marks_examiner1 = db.Column(db.Float)
    fe_pr_marks_examiner1 = db.Column(db.Float)

    ca_marks_examiner2 = db.Column(db.Float)
    fe_th_marks_examiner2 = db.Column(db.Float)
    fe_pr_marks_examiner2 = db.Column(db.Float)

    # Final marks after exam board adjustments
    final_ca_marks = db.Column(db.Float)
    final_fe_th_marks = db.Column(db.Float)
    final_fe_pr_marks = db.Column(db.Float)
    final_total_marks = db.Column(db.Float)
    
    # Grades for each component and the final grade
    ca_grade = db.Column(db.String(2))
    fe_th_grade = db.Column(db.String(2))
    fe_pr_grade = db.Column(db.String(2))
    final_grade = db.Column(db.String(2))
    
    # Approval flags to lock changes post-release
    is_approved_by_exam_board = db.Column(db.Boolean, default=False)
    is_approved_by_dean = db.Column(db.Boolean, default=False)
    is_released_to_student = db.Column(db.Boolean, default=False)

    # Attendance tracking
    attendance_CA = db.Column(db.Boolean, default=True)
    attendance_FE_TH = db.Column(db.Boolean, default=True)
    attendance_FE_PR = db.Column(db.Boolean, default=True)
    
    # Relationships
    student = relationship("Student", back_populates="registrations")
    exam = relationship("Exam", back_populates="registrations")
    course = relationship("Course", back_populates="registrations")

    # Unique constraint for max attempt rule
    __table_args__ = (
        UniqueConstraint('student_no', 'exam_id', name='unique_exam_attempt_per_student'),
    )

    def update_grades_and_attendance(self, CA_score, FE_TH_score=None, FE_PR_score=None):
        """Update grades and final total based on scores and attendance."""
        
        # Determine grades based on attendance
        self.ca_grade = "AB" if not self.attendance_CA else self.calculate_grade(CA_score)
        self.fe_th_grade = "AB" if not self.attendance_FE_TH else self.calculate_grade(FE_TH_score)
        self.fe_pr_grade = "AB" if not self.attendance_FE_PR else self.calculate_grade(FE_PR_score)
        
        # Calculate final total grade based on attendance and grades
        if "AB" in [self.ca_grade, self.fe_th_grade, self.fe_pr_grade]:
            self.final_grade = "AB"
        else:
            self.final_grade = self.calculate_final_total_grade(CA_score, FE_TH_score, FE_PR_score)
        
        db.session.commit()

    def calculate_final_total_grade(self, CA_score, FE_TH_score, FE_PR_score):
        """Calculate final grade based on weighted scores for the components."""
        weights = {
            "CA": self.course.ca_weight,
            "FE_TH": self.course.fe_th_weight,
            "FE_PR": self.course.fe_pr_weight
        }
        total_score = (
            (CA_score or 0) * weights["CA"] +
            (FE_TH_score or 0) * weights["FE_TH"] +
            (FE_PR_score or 0) * weights["FE_PR"]
        ) / sum(weights.values())
        
        return self.calculate_grade(total_score)
