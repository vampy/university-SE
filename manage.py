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

    test_course_algebra = Course(name="Algebra")
    test_course_calculus = Course(name="Calculus")
    test_course_arhitecture = Course(name="Computer Arhitecture")
    test_course_se = Course(name="SE")
    test_course_os = Course(name="OS")
    test_course_geometry = Course(name="Geometry")
    test_course_graphs = Course(name="Graphs Algorithms")
    test_course_os2 = Course(name="OS2")
    test_course_dbms = Course(name="DBMS")
    test_course_ai = Course(name="AI")
    test_course_networks = Course(name="Computer Networks")

    test_degree = Degree(name="Computer Science", type_id=DegreeType.UNDERGRADUATE)
    test_degree.courses.extend(
        [test_course_algebra, test_course_calculus, test_course_arhitecture, test_course_se, test_course_os, test_course_os2,
         test_course_geometry, test_course_graphs, test_course_dbms, test_course_ai, test_course_networks])
    test_department.degrees.append(test_degree)

    test_semester1 = Semester(name="Autumn 2013", year=2013, date_start=date(2013, 10, 1), date_end=date(2014, 2, 15))
    test_semester1.courses.extend([test_course_algebra, test_course_calculus, test_course_arhitecture])

    # leave second semester empty on purpose
    test_semester2 = Semester(name="Spring 2014", year=2013, date_start=date(2014, 2, 20), date_end=date(2014, 6, 15))
    test_semester2.courses.extend([test_course_os, test_course_geometry, test_course_graphs])

    test_semester3 = Semester(name="Autumn 2014", year=2014, date_start=date(2014, 10, 1), date_end=date(2015, 2, 15))
    test_semester3.courses.extend([test_course_dbms, test_course_os2])

    test_semester4 = Semester(name="Spring 2015", year=2014, date_start=date(2015, 2, 20), date_end=date(2015, 6, 15))
    test_semester4.courses.extend([test_course_ai, test_course_networks, test_course_se])

    test_semester5 = Semester(name="Autumn 2015", year=2015, date_start=date(2015, 10, 1), date_end=date(2016, 2, 15))
    test_semester6 = Semester(name="Spring 2016", year=2015, date_start=date(2016, 2, 20), date_end=date(2016, 6, 15))

    test_dperiod1 = DegreePeriod()
    test_dperiod1.degree = test_degree
    test_dperiod1.semester_start = test_semester1
    test_dperiod1.semester_end = test_semester4

    db.session.add_all([test_semester1, test_semester2, test_semester3, test_semester4, test_semester5, test_semester6,
                        test_degree, test_department, test_dperiod1])

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

    db.session.add_all([test_group, test_user, test_teacher, test_chief_department, test_admin])

    # add Contracts
    test_user_degree = test_user.get_default_period().degree
    for semester in [test_semester1, test_semester2]:
        db.session.add(ContractSemester(student=test_user, semester=semester, degree=test_user_degree))

    # add enrollments to all users, aka user has contract signed
    semesters = [test_semester1, test_semester2, test_semester3, test_semester4]

    for semester in semesters:
        for course in semester.courses:
            if course.degree == test_user_degree:
                db.session.add(Enrollment(student=test_user, semester=semester, course=course))

    # add teaches
    test_teaches1 = Teaches(teacher=test_teacher, semester=test_semester3, course=test_course_se)
    test_teaches2 = Teaches(teacher=test_teacher, semester=test_semester3, course=test_course_os2)
    db.session.add_all([test_teaches1, test_teaches2])

    db.session.commit()

    # print(test_user.degree_periods.first().degree)
    # print(test_user.get_semesters_for_period(test_user.get_default_period()))
    # print(Semester.get_semesters(date(2013, 10, 1), date(2015, 2, 15)))
    print('DB initialized')

if __name__ == "__main__":
    manager.run()
