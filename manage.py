#!/usr/bin/python3
from datetime import date
import random

from school import create_app
from school.user import User
from school.user.models import Role
from school.models import *
from flask.ext.script import Manager
from school.extensions import db

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
    # generate_data_v1()
    generate_data_v2()


def generate_data_v2():
    # DEPARTMENT
    # =========================================================================
    test_department = Department(name="Math/Computer Science")

    # COURSE
    # =========================================================================
    #                   SEMESTER 1
    course_names_cs = ["Algebra", "Calculus", "Computer Architecture", "Fundamentals of programming",
                       "Computational Logic",
                       # SEMESTER 2
                       "OOP", "OS", "Geometry", "Graphs Algorithms", "Data Structures and Algorithms",
                       # SEMESTER 3
                       "Advanced Programming Methods", "Distributed Operating Systems", "Databases",
                       "Functional and Logic Programming", "Probability and statistics",
                       # SEMESTER 4
                       "DBMS", "Artificial Intelligence", "Software Engineering", "Computer Networks",
                       "Individual Project",
                       # SEMESTER 5
                       " Graphics"]
    courses = []
    for course_name in course_names_cs:
        courses.append(Course(name=course_name))

    # DEGREE
    # =========================================================================

    test_degree = Degree(name="Computer Science", type_id=DegreeType.UNDERGRADUATE)
    test_degree.courses.extend(courses)
    test_department.degrees.append(test_degree)

    # SEMESTER
    # =========================================================================
    semester_names = ["Autumn ", "Spring "]
    years = [2013, 2014, 2015, 2016]
    semesters = []
    for i in range(0, len(years)):
        semesters.append(Semester(
            name=semester_names[0] + years[i].__str__(),
            year=years[i],
            date_start=date(years[i], 10, 1),
            date_end=date(years[i] + 1, 2, 15)
        ))
        semesters.append(Semester(
            name=semester_names[1] + (years[i] + 1).__str__(),
            year=years[i],
            date_start=date(years[i] + 1, 2, 20),
            date_end=date(years[i] + 1, 6, 15)
        ))

    db.session.add_all(semesters)
    db.session.commit()

    # SEMESTER_COURSE
    # =========================================================================

    first = True
    for semester in semesters:
        if first:
            semester.courses.extend(courses[0:5])
            semester.courses.extend(courses[10:15])
            first = False
        else:
            semester.courses.extend(courses[5:10])
            semester.courses.extend(courses[15:20])
            first = True

    # LANGUAGE
    # =========================================================================

    english_language = Language(name="English")
    db.session.add(english_language)
    db.session.commit()

    # DEGREE PERIOD
    # =========================================================================
    degree_periods = []
    no_of_degree_periods = 2
    for i in range(0, no_of_degree_periods * 2, 2):
        degree_periods.append(DegreePeriod())
        degree_periods[-1].degree = test_degree
        degree_periods[-1].language_id = english_language.id
        degree_periods[-1].semester_start = semesters[i]
        degree_periods[-1].semester_end = semesters[i + 5]

    db.session.add_all(degree_periods)
    db.session.add(test_department)

    # USERS
    # =========================================================================

    # TEACHER AND TEACHES
    # =========================================================================
    random_teacher_names = ["Keira Wrinkle", "Lurline Leary", "Jazmine Bender", "Lissette Rayes", "Mindy Trussell",
                            "Joellen Findlay", "Avelina Stoudemire", "Edward Chadbourne", "Ilda Byrns", "Kelli Wolford",
                            "Omer Folger", "Holly Donelson", "Gregorio Faris", "Jenee Fleischman", "Janel Tafoya",
                            "Kelsi Callihan", "Lyle Iverson", "Demetria Freitag", "Guy Ryant", "Adan Leachman"]
    test_teacher = User(
        username="teacher",
        password="teacher",
        realname="Test Teacher",
        email="dan@chiorean.com",
        role_id=Role.TEACHER
    )
    test_teacher2 = User(
        username="teacher2",
        password="teacher2",
        realname="Test Teacher 2",
        email="dan2@chiorean.com",
        role_id=Role.TEACHER
    )
    teachers = []
    for random_teacher_name in random_teacher_names:
        credentials = random_teacher_name.split(" ")
        teachers.append(User(
            username=credentials[0].lower(),
            password=credentials[1].lower(),
            realname=random_teacher_name,
            email=random_teacher_name.replace(" ", "").lower() + "@gmail.com",
            role_id=Role.TEACHER

        ))
        teachers[-1].qualification.append(Qualification())
        teachers[-1].department_teacher.append(test_department)

    db.session.add_all(teachers)
    db.session.commit()

    teaches = []
    for i in range(0, len(teachers)):
        if i % 10 == 0:
            semester_start = 0
        elif i % 5 == 0:
            semester_start = 1
        for j in range(semester_start, semester_start + 3, 2):
            teaches.append(Teaches(teacher=teachers[i], semester=semesters[j], course=courses[i]))

    db.session.add_all(teaches)
    db.session.commit()

    # CHIEF_DEPARTMENT
    # =========================================================================

    test_chief_department = User(
        username="cd",
        password="cd",
        realname="Dan Chiorean",
        email="danchiorean@cd.com",
        role_id=Role.CHIEF_DEPARTMENT
    )
    # ADMIN
    # =========================================================================

    test_admin = User(
        username="admin",
        password="admin",
        realname="Admin",
        email="admin@example.com",
        role_id=Role.ADMIN
    )
    # STUDENT
    # =========================================================================
    random_student_names = ["Shemeka Rolland", "Jaclyn Milera", "Shu Jennison",
                            "Tomeka Bolten", "Bonita Crose", "Merle Guess", "Tomiko Lape", "Tommie Leclerc",
                            "Lenita Omar", "Norris Gaut", "Lashawn Puryear", "Jacalyn Chaput", "Susy Tigner",
                            "Delphine Holbrook", "Celeste Evensen", "Wilburn Lucky", "Perry Ratledge",
                            "Jolanda Orchard",
                            "Ivory Guidry", "Earlean Odle", "Hilaria Edman", "Lachelle Vanover", "Twila Maine",
                            "Kam Timoteo", "Audria Lamkin", "Dahlia Donelson", "Ayesha Fessenden", "Linnie Luckett",
                            "Jason Dynes", "Kyle Snider", "Sena Collins", "Erika Michell", "Misha Moncayo",
                            "Hilde Nappi", "Susanna Conigliaro", "Kristal Blassingame", "Chantell Paille",
                            "Lakeshia Novy",
                            "Cassaundra Boudreaux", "Onita Livengood", "Scot Lachermeier", "Jammie River",
                            "Leandra Muse",
                            "Leia Lunday", "Elvin Cosey", "Christene Formica", "Kassandra Strothers", "Zane Mcgahee",
                            "Emmett Mazzei", "Aleta Wygant", "Shannon Fausnaught", "Melynda Hornsby", "Dawn Talarico",
                            "Javier Stallcup", "Rosaline Morein", "Laine Buss", "Roselle Largent", "Claudette Gourd",
                            "Lino Hynson", "Margeret Prasad", "Sherry Dunaway", "Dorethea Deshaies", "Fredda Mawson",
                            "Lazaro Rosalez", "Thomasina Lape", "Geoffrey Zylstra", "Dwana Halterman", "Tiffani Hieb",
                            "Tammy Mackey", "Ninfa Simms", "Drucilla Militello", "Constance Blaylock",
                            "Adrian Forrester",
                            "Talia Rome", "Amado Vibbert", "Mei Lai", "Gilberte Vassell", "Lesia Brizendine",
                            "Weldon Grady", "Dian Loo", "Megan Peralta", "Sharan Spight", "Fannie Nath",
                            "Amber Yarberry", "Gisela Moisan", "Alphonse Brokaw", "Coletta Christen",
                            "Kimi Hildebrandt",
                            "Brenna Fleischer", "Vilma Yepez", "Delena Tobey", "Darron Alverez", "Darrin Beaudry",
                            "Ulrike Tann", "Danna Jordan", "Lesli Colas", "Harrison Ahl", "Victor Guan",
                            "Kymberly Waldeck", "Nola Foss", "Ressie Mancia", "Nita Parm", "Yang Queener",
                            "Berenice Mingo", "Terina Gentle", "Sarina Manes", "Cherie Lindner", "Jacquelyn Whitfield",
                            "Jamison Rosenfield", "Corie Haden", "Stefany Petrosky", "Jadwiga Schoenberger",
                            "Ruthe Laxton",
                            "Lajuana Mcmillian", "Xiao Broome", "Rocio Hendrix", "Emelina Messer", "Diego Yanez",
                            "Marti Sheaffer", "Domenica Corney", "Sonia Stromain", "Carly Meuser", "Melba Belville",
                            "Sharika Draughn", "Lorriane Oquinn", "Lucie Fullen", "Iona Simpler", "Hosea Swanberg",
                            "Ricki Traxler", "Freda Yang", "Maegan Odowd", "Vennie Sapienza", "Michale Quintero",
                            "Migdalia Kina", "Johanne Sturtevant", "Carolin Brough", "Tarsha Millener", "Chu Mignone",
                            "Willard Blass", "Douglas Mahi", "Royce Lamson", "Delana Wronski", "Kathleen Balke",
                            "Enid Gallimore", "Clarine Engberg ", "Francesco Hartline", "Darcey Greeno", "Jada Granato",
                            "Lucienne Alessi", "Janelle Montalto", "Maynard Farwell", "Saran Kaczynski",
                            "Rigoberto Greco",
                            "Sherryl Willetts", "Esta Gulbranson", "Malisa Lucier", "Imelda Pray", "Mirella Avant",
                            "Ozell Story", "Violet Bonilla", "Vonnie Priest", "Micah Fettig", "Bethany Gillins",
                            "Octavia Rodkey", "Yi Haithcock", "Kathie Depaola", "Khaleesi Steiner", "Stephanie Claflin",
                            "Salvatore Wisniewski", "Golda Haberle", "Lorri Chastain", "Wan Beisner", "Arden Archey",
                            "Marylin Ruffo", "Nida Commons", "Tamara Jaillet", "Lilliana Rosenbaum", "Hilario Gregorio",
                            "Erwin Gaskins", "Michelle Doherty", "Ariane Doolin", "Buford Stjames", "Jame Peaslee",
                            "Mamie Caplinger", "Lettie Pasquariello", "Rosalind Oesterling", "Carmen Bark",
                            "Orpha Degraff",
                            "Deloras Pomerleau", "Margaretta Buzbee", "Valda Applebaum", "Niesha Prosperie",
                            "Mildred Hoggard",
                            "Sybil Dykes", "Daniell Houchin", "Jamila Mass", "Daniella Trevino", "Danica Barriere"]

    test_user = User(
        username="test",
        password="test",
        realname="John Doe",
        email="test@example.com"
    )
    test_user2 = User(
        username="gabriel",
        password="gabriel",
        realname="Cramer Gabriel",
        email="cramergabriel@gmail.com"
    )

    students = []
    students.extend([test_user, test_user2])
    for random_name in random_student_names:
        credentials = random_name.split(" ")
        students.append(User(
            username=credentials[0].lower(),
            password=credentials[1].lower(),
            realname=random_name,
            email=random_name.replace(" ", "").lower() + "@gmail.com"

        ))
    db.session.add_all(students)
    db.session.commit()

    # GROUP
    # =========================================================================

    group_names = ["G921", "G922", "G923", "G924", "G925",
                   "G911", "G912", "G913", "G914", "G915"
                   # , "G931", "G932", "G933", "G934", "G935"
                   ]
    groups = []
    degree_period_index = 0

    # 5 groups per degree_period (year)
    group_milestone = 5
    for i in range(0, len(group_names)):
        groups.append(Group(
            name=group_names[i],
            degree_period=degree_periods[degree_period_index]
        ))
        if (i + 1) % group_milestone == 0:
            degree_period_index += 1

    group_index = 0
    degree_period_index = 0
    small_milestone = 20
    big_milestone = 100

    for i in range(0, len(students)):
        groups[group_index].students.append(students[i])
        students[i].degree_periods.append(degree_periods[degree_period_index])
        if (i + 1) % small_milestone == 0:
            group_index += 1
        if (i + 1) % big_milestone == 0:
            degree_period_index += 1

    db.session.add_all(groups)

    # CONTRACT SEMESTER
    # =========================================================================

    starting_semester_index = 0
    ending_semester_index = 4
    contract_semester = []
    for i in range(0, len(students)):
        for j in range(starting_semester_index, ending_semester_index):
            contract_semester.append(ContractSemester(
                student=students[i],
                semester=semesters[j],
                degree=test_degree
            ))
        if (i + 1) % big_milestone == 0:
            starting_semester_index += 2

    db.session.add_all(contract_semester)
    db.session.commit()

    # ENROLLMENT
    # =========================================================================

    courses_per_semester = 5
    no_of_courses_enrolled = 0
    semester_index = 0
    # first 100 students will be enrolled in 20 courses, next 100 students only in the first 10.
    enrollments = []
    for student in students[:100]:
        for course_index in range(0, len(courses) - 1):
            if course_index < 15:
                if random.randint(1, 10) > 5:
                    grade = 10
                else:
                    grade = random.randint(3, 10)

                enrollments.append(
                    Enrollment(student=student, semester=semesters[semester_index], course=courses[course_index],
                               grade=grade, date_grade=semesters[semester_index].date_end)
                )
            else:
                enrollments.append(
                    Enrollment(student=student, semester=semesters[semester_index], course=courses[course_index])
                )
            no_of_courses_enrolled += 1
            if no_of_courses_enrolled % courses_per_semester == 0:
                semester_index += 1

        semester_index = 0

    semester_index = 2
    # next 100 students only in the first 10.
    for student in students[100:]:
        for course_index in range(0, 10):
            if course_index < 5:
                if random.randint(1, 10) > 5:
                    grade = 10
                else:
                    grade = random.randint(3, 10)

                enrollments.append(
                    Enrollment(student=student, semester=semesters[semester_index], course=courses[course_index],
                               grade=grade, date_grade=semesters[semester_index].date_end)
                )
            else:
                enrollments.append(
                    Enrollment(student=student, semester=semesters[semester_index], course=courses[course_index])
                )
            no_of_courses_enrolled += 1
            if no_of_courses_enrolled % courses_per_semester == 0:
                semester_index += 1
        semester_index = 2


    db.session.add_all(enrollments)

    test_chief_department.department_cd.append(test_department)
    test_teacher.department_teacher.append(test_department)
    test_teacher.qualification.append(Qualification())
    test_teacher2.department_teacher.append(test_department)
    test_teacher2.qualification.append(Qualification())

    db.session.add_all([test_teacher2, test_teacher,
                        test_chief_department, test_admin])

    # add optional courses
    course_aop, teaches_aop = test_teacher.add_optional_course("AOP", test_degree.id, semesters[3].id, True)
    test_teacher.add_optional_course("Security", test_degree.id, semesters[4].id, True)
    test_teacher2.add_optional_course("Design Patterns", test_degree.id, semesters[4].id, True)
    # Enroll the first 100 students in aop.
    enrollments_aop = []
    for student in students[:100]:
        enrollments_aop.append(Enrollment(student=student, semester=teaches_aop.semester, course=course_aop))

    db.session.add_all(enrollments_aop)

    db.session.commit()

    print('DB initialized')


def generate_data_v1():
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
    test_course_networks2 = Course(name="Computer Networks2")
    test_course_graphics = Course(name="Graphics")

    test_degree = Degree(name="Computer Science", type_id=DegreeType.UNDERGRADUATE)
    test_degree.courses.extend(
        [test_course_algebra, test_course_calculus, test_course_arhitecture, test_course_se, test_course_os,
         test_course_os2, test_course_geometry, test_course_graphs, test_course_dbms, test_course_ai,
         test_course_networks, test_course_graphics, test_course_networks2])
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
    test_semester5.courses.extend([test_course_networks2, test_course_graphics])

    test_semester6 = Semester(name="Spring 2016", year=2015, date_start=date(2016, 2, 20), date_end=date(2016, 6, 15))

    test_language = Language(name="English")
    db.session.add(test_language)
    db.session.commit()
    test_dperiod1 = DegreePeriod()
    test_dperiod1.degree = test_degree
    test_dperiod1.language_id = test_language.id
    test_dperiod1.semester_start = test_semester1
    test_dperiod1.semester_end = test_semester6

    db.session.add_all([test_semester1, test_semester2, test_semester3, test_semester4, test_semester5, test_semester6,
                        test_degree, test_department, test_dperiod1])

    # Add users
    # students
    test_user = User(
        username="test",
        password="test",
        realname="John Doe",
        email="test@example.com"
    )
    test_user2 = User(
        username="gabriel",
        password="gabriel",
        realname="Cramer Gabriel",
        email="cramergabriel@gmai.com"
    )
    test_user3 = User(
        username="harap",
        password="alb",
        realname="Harap Alb",
        email="harapalb@gmail.com"
    )
    # teacher
    test_teacher = User(
        username="teacher",
        password="teacher",
        realname="Test Teacher",
        email="dan@chiorean.com",
        role_id=Role.TEACHER
    )
    test_teacher2 = User(
        username="teacher2",
        password="teacher2",
        realname="Test Teacher 2",
        email="dan2@chiorean.com",
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
    test_group = Group(name="921", degree_period=test_dperiod1)
    test_group.students.append(test_user)
    test_group.students.append(test_user2)
    test_group2 = Group(name="922", degree_period=test_dperiod1)
    test_group2.students.append(test_user3)
    test_chief_department.department_cd.append(test_department)
    test_teacher.department_teacher.append(test_department)
    test_teacher.qualification.append(Qualification())
    test_teacher2.department_teacher.append(test_department)
    test_teacher2.qualification.append(Qualification())
    test_user.degree_periods.append(test_dperiod1)
    test_user2.degree_periods.append(test_dperiod1)
    test_user3.degree_periods.append(test_dperiod1)

    db.session.add_all([test_group, test_group2, test_user, test_user2, test_user3, test_teacher2, test_teacher,
                        test_chief_department, test_admin])

    # add enrollments to all users, aka user has contract signed
    semesters = [test_semester1, test_semester2, test_semester3, test_semester4]

    # add Contracts
    test_user_degree = test_user.get_default_period().degree
    for semester in semesters:
        db.session.add(ContractSemester(student=test_user, semester=semester, degree=test_user_degree))

    test_user2_degree = test_user2.get_default_period().degree
    for semester in [test_semester1, test_semester2]:
        db.session.add(ContractSemester(student=test_user2, semester=semester, degree=test_user2_degree))

    test_user3_degree = test_user3.get_default_period().degree
    for semester in [test_semester1, test_semester2]:
        db.session.add(ContractSemester(student=test_user3, semester=semester, degree=test_user3_degree))

    # add enrollments to all users, aka user has contract signed
    semesters = [test_semester1, test_semester2, test_semester3, test_semester4]

    students = [test_user, test_user2, test_user3]
    student_degrees = [test_user_degree, test_user2_degree, test_user3_degree]

    for semester in semesters:
        for course in semester.courses:
            # zip: the lists should have the same length.
            for student, student_degree in zip(students, student_degrees):
                if course.degree == student_degree:
                    db.session.add(Enrollment(student=student, semester=semester, course=course,
                                              grade=random.randint(3, 10)))

    # add teaches
    test_teaches1 = Teaches(teacher=test_teacher, semester=test_semester3, course=test_course_se)
    test_teaches2 = Teaches(teacher=test_teacher, semester=test_semester3, course=test_course_os2)
    test_teaches3 = Teaches(teacher=test_chief_department, semester=test_semester3, course=test_course_dbms)
    db.session.add_all([test_teaches1, test_teaches2, test_teaches3])

    db.session.commit()

    # add optional courses
    course_aop, teaches_aop = test_teacher.add_optional_course("AOP", test_degree.id, test_semester4.id, True)
    test_teacher.add_optional_course("Security", test_degree.id, test_semester5.id, True)
    test_teacher2.add_optional_course("Design Patterns", test_degree.id, test_semester5.id, True)
    db.session.add(Enrollment(student=test_user, semester=teaches_aop.semester, course=course_aop))
    db.session.commit()

    # print(test_user.degree_periods.first().degree)
    # print(test_user.get_semesters_for_period(test_user.get_default_period()))
    # print(Semester.get_semesters(date(2013, 10, 1), date(2015, 2, 15)))
    print('DB initialized')


if __name__ == "__main__":
    manager.run()
