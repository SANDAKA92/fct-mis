import csv
from umis import create_app, db
from umis.models import ExamResult, User, Student  # Import your model
from sqlalchemy.exc import IntegrityError

app = create_app()

def convert_to_float(value):
    """Helper function to convert empty strings to None or float."""
    try:
        return float(value) if value != '' else None
    except ValueError:
        return None
'''
def load_data_student(csv_file):
    with app.app_context():  # Create an application context
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Create an instance in User
                user = User(
                    reg_no=row['studentNo'],
                    email=row['email'],
                    is_admin=False,
                    user_type='student'
                )
                db.session.add(user)
                db.session.flush()  # Get the user.id 

                phoneNo =  row['phone_no']
                if not phoneNo:  # If phone_no is empty or invalid
                    phoneNo = None  # Set it to None to insert as NULL

                # Create an instance of Student for each row in the CSV
                student = Student(
                    student_no=row['studentNo'],
                    nic=None,
                    email=row['email'],
                    phone_no=phoneNo,
                    name=row['Name'],
                    entered_acYear=row['ent_acYear'],
                    reg_status=row['reg_stat'],
                )
                db.session.add(student)  # Add the result to the session
            db.session.commit()  # Commit all the changes at once
'''

def load_data_student(csv_file):
    with app.app_context():  # Create an application context
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Check if the user already exists
                    user = User.query.filter_by(reg_no=row['studentNo'], email=row['email']).first()
                    if not user:
                        user = User(
                            reg_no=row['studentNo'],
                            email=row['email'],
                            is_admin=False,
                            user_type='student'
                        )
                        db.session.add(user)
                        db.session.flush()  # Get the user.id

                    # Check if the student already exists
                    student = Student.query.filter_by(student_no=row['studentNo']).first()
                    if not student:
                        phoneNo = row['phone_no'].strip() if row['phone_no'].strip() else None
                        
                        # Create an instance of Student for each row in the CSV
                        student = Student(
                            student_no=row['studentNo'],
                            nic=None,
                            email=row['email'],
                            phone_no=phoneNo,
                            name=row['Name'],
                            entered_acYear=row['ent_acYear'],
                            reg_status=row['reg_stat'],
                        )
                        db.session.add(student)

                    # Commit after adding the user and student
                    db.session.commit()

                except IntegrityError as e:
                    db.session.rollback()  # Rollback in case of integrity errors (e.g., duplicate entries)
                    print(f"IntegrityError processing row {row}: {e}")

                except Exception as e:
                    db.session.rollback()  # Rollback for any other kind of exception
                    print(f"Error processing row {row}: {e}")



def load_data_examresults(csv_file):
    with app.app_context():  # Create an application context
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Create an instance of ExamResult for each row in the CSV
                exam_result = ExamResult(
                    examId=row['examId'],
                    degreeCode=row['degreeCode'],
                    acYear=row['acYear'],
                    level=row['level'],
                    semester=row['semester'],
                    examStatusId=row['examStatusId'],
                    attempt=row['attempt'],
                    studentNo=row['studentNo'],
                    courseCode=row['courseCode'],
                    ca_marks=convert_to_float(row['ca']),  # Convert to float or None
                    th_marks=convert_to_float(row['th']),  # Convert to float or None
                    pr_marks=convert_to_float(row['pr']),  # Convert to float or None
                    total_marks=convert_to_float(row['total_marks']),  # Convert to float or None
                    grade=row['grade'],
                    ca_grade=row['caGrade'],
                    th_grade=row['thGrade'],
                    pr_grade=row['prGrade'],
                    grd_comments=row['grd-comments'],
                )
                db.session.add(exam_result)  # Add the result to the session
            db.session.commit()  # Commit all the changes at once

if __name__ == '__main__':
    load_data_student('../bet_students.csv')  # Replace with your CSV file
    load_data_examresults('../exmresults.csv')  # Replace with your CSV file

