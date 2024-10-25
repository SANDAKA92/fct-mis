from .models import db, ExamResult, GradeLetterInfo, DegreeCourseReq  # Import necessary models
from sqlalchemy import func
from flask import current_app as app

def get_best_grade(student_no, course_code, relevant_semesters):
    """
    This function retrieves the best grade (based on highest total marks) 
    for a given student in a specific course.
    """
    # Query the highest total marks for a given course across relevant semesters
    best_attempt = ExamResult.query.filter_by(studentNo=student_no, courseCode=course_code)\
                                   .filter((ExamResult.level, ExamResult.semester).in_(relevant_semesters))\
                                   .order_by(ExamResult.total_marks.desc()).first()

    # Return None if no results found
    if not best_attempt:
        return None

    # Return the grade of the attempt with the highest total marks
    return best_attempt.grade

# Function to calculate GPA
def calculate_gpa(student_no, degree_code):
    # Step 1: Get the highest total_marks for each courseCode
    subquery = (
        db.session.query(
            ExamResult.courseCode,
            func.max(ExamResult.total_marks).label('max_total_marks')
        )
        .filter(ExamResult.studentNo == student_no)
        .group_by(ExamResult.courseCode)
    ).subquery()

    # Step 2: Join with ExamResult to get corresponding grade letters
    exam_results = (
        db.session.query(ExamResult.courseCode, ExamResult.grade_letter)
        .join(subquery, (ExamResult.courseCode == subquery.c.courseCode) &
               (ExamResult.total_marks == subquery.c.max_total_marks))
        .filter(ExamResult.studentNo == student_no)
    ).all()

    # Step 3: Initialize variables for GPA calculation
    total_gpv = 0.0
    total_credits = 0.0

    for course_code, grade_letter in exam_results:
        # Get GPV for the grade letter
        gpv_info = db.session.query(GradeLetterInfo.gpv).filter_by(grade_letter=grade_letter, degree_code=degree_code).first()
        
        # Get credits for the course
        credits_info = db.session.query(DegreeCourseReq.gpaCredits).filter_by(course_code=course_code, degree_code=degree_code).first()

        if gpv_info and credits_info:
            gpv = gpv_info.gpv
            credits = credits_info.gpaCredits
            
            # Weighted sum calculation
            total_gpv += gpv * credits
            total_credits += credits

    # Step 4: Calculate GPA
    if total_credits > 0:
        gpa = total_gpv / total_credits
        return round(gpa, 2)  # Round to 2 decimal places
    else:
        return 0.0  # No credits means GPA cannot be calculated

# Function to check graduation criteria
def grad_check(student_no):
    # Logic for checking graduation criteria

# Function to check progression criteria for enrollment to the 5th semester
def progression_check(student_no, degree_code):
    # Query for compulsory courses in level 1 semester 1, level 1 semester 2, and level 2 semester 1
    compulsory_courses = DegreeCourseReq.query.filter_by(degree_code=degree_code, compulsory=True).all()
    
    # Define the semesters for progression check (Level 1 sem 1, Level 1 sem 2, Level 2 sem 1)
    relevant_semesters = [(1, 1), (1, 2), (2, 1)]  # (Level, Semester)

    # Initialize GPA calculation variables
    total_points = 0
    total_credits = 0
    total_credits_failed = 0

    # Check for 'E' grades in compulsory courses
    for course in compulsory_courses:
        grade = get_best_grade(student_no, course.courseCode, relevant_semesters)
        
        # If 'E' grade is found, fail progression check
        if grade == 'E':
            total_credits_failed += 1

        # Continue GPA calculation if result exists
        if grade:
            # Get GPV from GradeLetterInfo table for the student's degree code and grade
            gpv = GradeLetterInfo.query.filter_by(degreeCode=degree_code, gradeLetter=grade).first().gpv
            
            # Get the number of GPA credits for the course
            credits = course.gpaCredits
            
            # Calculate weighted points
            total_points += gpv * credits
            total_credits += credits

    # Calculate GPA
    gpa = total_points / total_credits

    # Check if GPA is greater than or equal to 2.0

    # If all checks pass
    return total_credis_failed, gpa 

# Function to generate transcript using LaTeX
def gen_transcript(student_no):
    # LaTeX code to generate transcript

# Function to generate progression report using LaTeX
def gen_progress_report(student_no):
    # LaTeX code to generate progression report

# Function to generate mark sheet for final comprehensive exam
def gen_marksheet(course_code):
    # LaTeX code to generate marksheet

# Function to generate results release documents for exam board approval
def gen_results_release_docs(course_code):
    # LaTeX code to generate results release documents

