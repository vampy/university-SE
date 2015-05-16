#!/usr/bin/python3
from school import create_app
from school.user import User
from school.user.models import Role
from school.models import *
from flask.ext.script import Manager
from school.extensions import db
from datetime import date

app = create_app()
manager = Manager(app)


@manager.command
def run():
    """
    Run local app
    """
    app.run()


@manager.command
def init():
    """
    Init/reset database
    """
    db.drop_all()
    db.create_all()

    # Add department, semester, etc
    test_department = Department(name="Math/Computer Science")

    test_course1 = Course(name="SE", is_optional=True)
    test_course2 = Course(name="OS", is_optional=True)
    test_course3 = Course(name="DBMS", is_optional=True)

    test_degree = Degree(name="Computer Science", type_id=DegreeType.UNDERGRADUATE)
    test_degree.courses.extend([test_course1, test_course2, test_course3])
    test_department.degrees.append(test_degree)

    test_semester1 = Semester(name="Autumn 2014", year=2015,
                              date_start=date(2014, 10, 1), date_end=date(2015, 2, 15))
    test_semester1.courses.extend([test_course1, test_course2])

    test_semester2 = Semester(name="Spring 2015", year=2015,
                              date_start=date(2015, 2, 20), date_end=date(2015, 6, 15))
    test_semester2.courses.extend([test_course1, test_course2, test_course3])

    test_dperiod1 = DegreePeriod()
    test_dperiod1.degree = test_degree
    test_dperiod1.semester_start = test_semester1
    test_dperiod1.semester_end = test_semester2

    db.session.add(test_degree)
    db.session.add(test_department)
    db.session.add(test_semester1)
    db.session.add(test_semester2)
    db.session.add(test_dperiod1)

    # Add users
    # student
    test_user = User(
        username="test",
        password="test",
        realname="John Doe",
        email="test@example.com"
    )
    # teacher
    test_teacher = User(
        username="teacher",
        password="teacher",
        realname="Test Teacher",
        email="dan@chiorean.com",
        role_id=Role.TEACHER
    )
    # chief_department

    test_chief_department = User(
        username="cd",
        password="cd",
        realname="Dan Chiorean",
        email="danchiorean@cd.com",
        role_id=Role.CHIEF_DEPARTMENT
    )
    # admin
    test_admin = User(
        username="admin",
        password="admin",
        realname="Admin",
        email="admin@example.com",
        role_id=Role.ADMIN
    )

    # add additional options to each user
    test_group = Group(name="911")
    test_group.students.append(test_user)
    test_chief_department.department.append(test_department)
    test_user.degree_periods.append(test_dperiod1)

    db.session.add(test_group)
    db.session.add(test_user)
    db.session.add(test_teacher)
    db.session.add(test_chief_department)
    db.session.add(test_admin)

    # add enrollments
    test_enrollment1 = Enrollment(student=test_user, semester=test_semester1, course=test_course1)
    test_enrollment2 = Enrollment(student=test_user, semester=test_semester1, course=test_course2)
    test_enrollment3 = Enrollment(student=test_user, semester=test_semester2, course=test_course1)
    test_enrollment4 = Enrollment(student=test_user, semester=test_semester2, course=test_course3)
    
    db.session.add(test_enrollment1)
    db.session.add(test_enrollment2)
    db.session.add(test_enrollment3)
    db.session.add(test_enrollment4)

    # add teaches
    test_teaches1 = Teaches(teacher=test_teacher, semester=test_semester1, course=test_course1)
    test_teaches2 = Teaches(teacher=test_teacher, semester=test_semester1, course=test_course2)
    db.session.add(test_teaches1)
    db.session.add(test_teaches2)

    db.session.commit()

    # print(test_user.degree_periods.first().degree)
    print('DB initialized')

if __name__ == "__main__":
    manager.run()
