from datetime import datetime
from sqlalchemy import Enum as SQLAEnum, ForeignKey, UniqueConstraint, DateTime, Float, Integer
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import enum

db = SQLAlchemy()

# Enum for User Roles
class UserRole(enum.Enum):
    ADMIN = "admin"
    HOD = "hod"
    DEAN = "dean"
    EXAM_UNIT = "exam_unit"
    REGISTRAR = "registrar"
    STAFF = "staff"
    STUDENT = "student"

# Enum for CRUD Operations
class OperationType(enum.Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

# Enum for Exam Types
class ExamType(enum.Enum):
    THEORY = "theory"
    PRACTICAL = "practical"
    BOTH = "both"

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(20), unique=True)  # students - index no | staff - salary number
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    
    # Role field
    role = db.Column(SQLAEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    user_type = db.Column(db.String(10), nullable=False)  # "student" or "staff"

    # Relationships to Student and Staff models
    student = db.relationship('Student', backref='user', uselist=False)
    staff = db.relationship('Staff', backref='user', uselist=False)

    # Permission Checks
    def has_role(self, *roles):
        """Check if the user has one of the specified roles."""
        return self.role in roles

    def is_admin(self):
        return self.role == UserRole.ADMIN

    def is_hod(self):
        return self.role == UserRole.HOD

    def is_dean(self):
        return self.role == UserRole.DEAN

    def is_exam_unit(self):
        return self.role == UserRole.EXAM_UNIT

    def is_registrar(self):
        return self.role == UserRole.REGISTRAR

# Audit Log Model to track CRUD operations
class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    operation = db.Column(SQLAEnum(OperationType), nullable=False)  # create, read, update, delete
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)  # ID of the record in the target table
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    changes = db.Column(db.Text, nullable=True)  # JSON or text field for storing changes in detail

    # Relationship with User to track who performed the operation
    user = relationship("User", backref="audit_logs")

# Faculty, Degree, and Department Models
class Faculty(db.Model):
    __tablename__ = 'faculties'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    degrees = relationship("Degree", back_populates="faculty")

class Degree(db.Model):
    __tablename__ = 'degrees'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    faculty_id = db.Column(db.Integer, ForeignKey('faculties.id'), nullable=False)
    faculty = relationship("Faculty", back_populates="degrees")
    courses = relationship("DegreeCourse", back_populates="degree")

class Pathway(db.Model):
    __tablename__ = 'pathways'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    degree_id = db.Column(db.Integer, ForeignKey('degrees.id'), nullable=False)
    courses = relationship("PathwayCourse", back_populates="pathways")

class semester(db.Model):
    __tablename__ = 'semesters'
    id = db.Column(db.Integer, primary_key=True)
    ac_year = db.Column(db.String(10), nullable=False)
    start_date = db.Column(DateTime, nullable=False)
    end_date = db.Column(DateTime, nullable=False)
    course_drop_date = db.Column(DateTime, nullable=False)
    mid_start_date = db.Column(DateTime, nullable=False)
    fe_start_date = db.Column(DateTime, nullable=False)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    courses = relationship("Course", back_populates="department")
    instructors = relationship("Instructor", back_populates="department")

# Course and CourseOffering Models
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, ForeignKey('departments.id'), nullable=False)
    department = relationship("Department", back_populates="courses")
    syllabus = db.Column(db.Text, nullable=False)
    lecture_hours = db.Column(db.Integer, nullable=False)
    practical_hours = db.Column(db.Integer, nullable=True)
    tutorial_hours = db.Column(db.Integer, nullable=True)
    credits = db.Column(db.Integer, nullable=False)

    # Weighting for assessments and exams
    ca_weight = db.Column(db.Float, nullable=False)
    final_theory_weight = db.Column(db.Float, nullable=False)
    final_practical_weight = db.Column(db.Float, nullable=True)

    degree_courses = relationship("DegreeCourse", back_populates="course")
    learning_outcomes = relationship("LearningOutcome", back_populates="course")

class DegreeCourse(db.Model):
    __tablename__ = 'degree_courses'
    id = db.Column(db.Integer, primary_key=True)
    degree_id = db.Column(db.Integer, ForeignKey('degrees.id'))
    course_id = db.Column(db.Integer, ForeignKey('courses.id'))
    is_compulsory = db.Column(db.Boolean, nullable=False)
    is_gpa = db.Column(db.Boolean, nullable=False)
    min_gpv = db.Column(db.Float, nullable=False)
    degree = relationship("Degree", back_populates="courses")
    course = relationship("Course", back_populates="degree_courses")

class PathwayCourse(db.Model):
    __tablename__ = 'pathway_courses'
    id = db.Column(db.Integer, primary_key=True)
    degree_id = db.Column(db.Integer, ForeignKey('degrees.id'))
    pathway_id = db.Column(db.Integer, ForeignKey('pathways.id'))
    course_id = db.Column(db.Integer, ForeignKey('courses.id'))
    is_compulsory = db.Column(db.Boolean, nullable=False)
    degree = relationship("Degree", back_populates="pathway_courses")
    course = relationship("Course", back_populates="pathway_courses")

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

# Instructor Model
class Instructor(db.Model):
    __tablename__ = 'instructors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, ForeignKey('departments.id'))
    department = relationship("Department", back_populates="instructors")

class InstructorCourseOffering(db.Model):
    __tablename__ = 'instructor_course_offering'
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, ForeignKey('instructors.id'))
    course_offering_id = db.Column(db.Integer, ForeignKey('course_offerings.id'))
    instructor = relationship("Instructor", back_populates="instructor_course_offering")
    course_offering = relationship("CourseOffering", back_populates="instructor_course_offering")

# Course Offering Model for Specific Semester
class CourseOffering(db.Model):
    __tablename__ = 'course_offerings'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, ForeignKey('courses.id'))
    degree_id = db.Column(db.Integer, ForeignKey('degrees.id'))
    ac_year = db.Column(db.String(10), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    course_outline_pdf = db.Column(db.Text, nullable=False)
    course_schedule_pdf = db.Column(db.Text, nullable=False)
    course = relationship("Course", back_populates="course_offerings")
    degree = relationship("Degree")
    sessions = relationship("Session", back_populates="offering", cascade="all, delete-orphan")
    exams = relationship("FinalExam", back_populates="course_offering")
    continuous_assessments = relationship("ContinuousAssessment", back_populates="course_offering")
    student_attendances = relationship("Attendance", back_populates="course_offering")
    student_registrations = relationship("StudentCourseRegistration", back_populates="course_offering")

    __table_args__ = (
        UniqueConstraint('course_id', 'degree_id', 'ac_year', 'level', 'semester', name='unique_course_offering'),
    )

### Session and Attendance ###
class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    offering_id = db.Column(db.Integer, ForeignKey('course_offerings.id'), nullable=False)
    instructor_id = db.Column(db.Integer, ForeignKey('instructors.id'))
    date = db.Column(db.Date, nullable=False)
    session_type = db.Column(db.String(20), nullable=False)  # "Lecture", "Tutorial", "Practical"
    hours = db.Column(db.Float, nullable=False)
    offering = relationship("CourseOffering", back_populates="sessions")
    instructor = relationship("Instructor", back_populates="sessions")
    attendances = relationship("Attendance", back_populates="sessions", cascade="all, delete-orphan")


# Learning Outcome, Continuous Assessment, and Mappings
class LearningOutcome(db.Model):
    __tablename__ = 'learning_outcomes'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, ForeignKey('courses.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    blooms_level = db.Column(db.Integer,nullable=False)
    solo_level = db.Column(db.Integer, nullable=False)
    course = relationship("Course", back_populates="learning_outcomes")
    ca_mappings = relationship("CAMapping", back_populates="learning_outcome")
    fe_mappings = relationship("FEMapping", back_populates="learning_outcome")

class ContinuousAssessment(db.Model):
    __tablename__ = 'continuous_assessments'
    id = db.Column(db.Integer, primary_key=True)
    course_offering_id = db.Column(db.Integer, ForeignKey('course_offerings.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    course_offering = relationship("CourseOffering", back_populates="continuous_assessments")
    student_scores = relationship("StudentCAScore", back_populates="continuous_assessment")

class CAMapping(db.Model):
    __tablename__ = 'ca_mappings'
    id = db.Column(db.Integer, primary_key=True)
    ca_id = db.Column(db.Integer, ForeignKey('continuous_assessments.id'))
    lo_id = db.Column(db.Integer, ForeignKey('learning_outcomes.id'))
    continuous_assessment = relationship("ContinuousAssessment", back_populates="ca_mapping")
    learning_outcome = relationship("LearningOutcome", back_populates="ca_mappings")

class StudentCAScore(db.Model):
    __tablename__ = 'student_ca_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, ForeignKey('student.student_no'), nullable=False)
    ca_id = db.Column(db.Integer, ForeignKey('continuous_assessments.id'), nullable=False)
    score = db.Column(db.Float, nullable=True)  # Score received for this CA component
    
    # Relationships
    student = relationship("Student", back_populates="ca_scores")
    continuous_assessment = relationship("ContinuousAssessment", back_populates="student_scores")

# Exam, Exam Question, Examiner, and Answer Script Models

class Examiner(db.Model):
    __tablename__ = 'examiners'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, ForeignKey('fina_exams.id'), nullable=False)
    examiner_id = db.Column(db.Integer, ForeignKey('instructors.id'), nullable=False)
    role = db.Column(SQLAEnum(UserRole), nullable=False)  # first_examiner, second_examiner, third_examiner
    exam = relationship("FinalExam", back_populates="examiners")
    instructor = relationship("Instructor")

class FinalExam(db.Model):
    __tablename__ = 'final_exams'
    id = db.Column(db.Integer, primary_key=True)
    course_offering_id = db.Column(db.Integer, ForeignKey('course_offerings.id'), nullable=False)
    exam_type = db.Column(SQLAEnum(ExamType), nullable=False) #Th - Theory | Pr - Practical | Vv - Viva
    exam_date = db.Column(DateTime, nullable=False)
    exam_time = db.Column(db.Time, nullable=False)
    exam_hall = db.Column(db.String(100), nullable=False)
    
    course_offering = relationship("CourseOffering", back_populates="final_exams")


class FEQuestion(db.Model):
    __tablename__ = 'fe_questions'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, ForeignKey('fina_exams.id'), nullable=False)
    question_num = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)  # Contribution of question to total exam marks
    exam = relationship("FinalExam", back_populates="fe_questions")

class FEMapping(db.Model):
    __tablename__ = 'fe_mappings'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, ForeignKey('fe_questions.id'))
    lo_id = db.Column(db.Integer, ForeignKey('learning_outcomes.id'))
    weight = db.Column(db.Float, nullable=False)
    exam_question = relationship("FEQuestion", back_populates="fe_mappings")
    learning_outcome = relationship("LearningOutcome", back_populates="fe_mappings")

class FEQuestionScore(db.Model):
    __tablename__ = 'fe_question_score'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, ForeignKey('fe_questions.id'))
    student_id = db.Column(db.Integer, ForeignKey('students.id'), nullable=False)
    first_examiner_marks = db.Column(db.Float)
    second_examiner_marks = db.Column(db.Float)
    third_examiner_marks = db.Column(db.Float)
    exam_question = relationship("FEQuestion", back_populates="fe_question_score")
    student = relationship("Student", back_populates="fe_question_score")

class FEScore(db.Model):
    __tablename__ = 'fe_question_score'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, ForeignKey('students.id'), nullable=False)
    first_examiner_FE_marks = db.Column(db.Float)
    second_examiner_FE_marks = db.Column(db.Float)
    third_examiner_FE_marks = db.Column(db.Float)
    total_CA_marks = db.Column(db.Float)
    student = relationship("Student", back_populates="fe_question_score")


class FEAdjustment(db.Model):
    __tablename__ = 'fe_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    exmboard_date = db.Column(DateTime, nullable=False)
    semester_id = db.Column(db.Integer, ForeignKey('semesters.id'), nullable=False)
    fe_question_id = db.Column(db.Integer, ForeignKey('fe_questions.id'), nullable=False)
    course_offering_id = db.Column(db.Integer, ForeignKey('course_offerings.id'), nullable=False)
    adjustment_type = db.Column(db.String(20), nullable=False)  # Marginal pass, failure rate adjustment
    adjustment_value = db.Column(db.Float, nullable=True)
    semester = relationship("Semester", back_populates="fe_adjustments")
    exam_question = relationship("FEQuestion", back_populates="fe_adjustments")
    course_offering = relationship("CourseOffering", back_populates="fe_adjustments")

class CAAdjustment(db.Model):
    __tablename__ = 'ca_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    exmboard_date = db.Column(DateTime, nullable=False)
    semester_id = db.Column(db.Integer, ForeignKey('semesters.id'), nullable=False)
    ca_id = db.Column(db.Integer, ForeignKey('continuous_assessments.id'), nullable=False)
    course_offering_id = db.Column(db.Integer, ForeignKey('course_offerings.id'), nullable=False)
    adjustment_type = db.Column(db.String(20), nullable=False)  # Marginal pass, failure rate adjustment
    adjustment_value = db.Column(db.Float, nullable=True)
    semester = relationship("Semester", back_populates="ca_adjustments")
    cas = relationship("ContinuousAssessments", back_populates="ca_adjustments")
    course_offering = relationship("CourseOffering", back_populates="ca_adjustments")


# Student Course Registration and Attendance Models
class StudentCourseRegistration(db.Model):
    __tablename__ = 'student_course_registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, ForeignKey('students.id'), nullable=False)
    course_offering_id = db.Column(db.Integer, ForeignKey('course_offerings.id'), nullable=False)
    registration_date = db.Column(DateTime, default=datetime.utcnow)
    course_offering = relationship("CourseOffering", back_populates="student_registrations")
    student = relationship("Student", back_populates="course_registrations")

class Student(db.Model):
    __tablename__ = 'student'
    
    id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    nic = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, unique=True)
    phone_no = db.Column(db.String(12), unique=True)
    name = db.Column(db.Text)

class DegreeRegistration(db.Model):
    __tablename__ = 'degree_registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, ForeignKey('students.id'), nullable=False)
    degree_id = db.Column(db.Integer, ForeignKey('degrees.id'), nullable=False)
    entered_acYear = db.Column(db.String(12))
    first_reg_date = db.Column(DateTime, default=datetime.utcnow)
    cGPA = db.Column(db.Float)
    reg_status = db.Column(db.String(2))  # RN - Registered Normal | UR - Unregistered | Sus - Suspended | Grd - Graduated
    student = relationship("Student", back_populates="degree_registrations")
    degree = relationship("Degree", back_populates="degree_registrations")

class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, ForeignKey('students.id'), nullable=False)
    reference_id = db.Column(db.Integer, nullable=False)  # Links to a session, CA, or FE
    reference_type = db.Column(db.String(20), nullable=False)  # "session", "CA", "FE"
    status = db.Column(db.Boolean, nullable=False)
    student = relationship("Student", back_populates="attendances")
    session = relationship("Session", back_populates="session_attendances")	
    ca = relationship("ContinuousAssessments", back_populates="ca_attendances")
    exam = relationship("FinalExam", back_populates="fe_attendances")
