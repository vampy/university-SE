from flask.ext.login import login_required, current_user
from flask import Blueprint, render_template, flash, redirect, url_for, request
from school.decorators import role_required
from school.config import FLASH_SUCCESS, FLASH_ERROR
from school.models import *
from school.user import User

course = Blueprint('course', __name__)


@course.route('/see_courses', methods=['GET', 'POST'])
@course.route('/see_courses/<int:semester_id>', methods=['GET', 'POST'])
@login_required
def see_courses(semester_id=None):
    if current_user.is_student():

        period = current_user.get_default_period()
        degree = period.degree
        semesters = User.get_semesters_for_period(period)

        if semester_id is None:  # use default, all semesters, enrolled with contract
            semester = None
            courses_enrolled = current_user.get_courses_enrolled(degree)
        else:  # has semester from url
            semester = Semester.get_by_id(semester_id)
            has_contract = current_user.has_contract_signed(semester, degree)
            courses_enrolled = []
            if has_contract:  # only display signed contracts for that semester
                courses_enrolled = current_user.get_courses_enrolled_semester(semester, degree)

        return render_template("course/see_courses.html",
                               semesters=semesters,
                               courses_enrolled=courses_enrolled,
                               selected_semester=semester)
    elif current_user.is_admin():

        departments = Department.query.order_by("name").all()

        seen_depts = set()
        depts = []
        courses_depts = []

        for department in departments:
            if department.name not in seen_depts:
                seen_depts.add(department.name)
                depts.append(department.name)
            for degree in department.degrees:
                for course in degree.courses:
                    dico = dict()
                    dico["course"] = course.name
                    dico["department"] = department.name
                    courses_depts.append(dico)

        return render_template("course/see_courses.html", total=courses_depts, depts=depts)

    elif current_user.is_teacher():

        courses = []
        for teach in current_user.teaches.all():
            courses.append(teach.course)

        return render_template("course/see_courses.html", courses=courses)

    elif current_user.is_chief_department():

        name_dp = "Math/Computer Science"
        department = Department.query.filter_by(name=name_dp).first()

        courses_depts = []

        for degree in department.degrees:
            for course in degree.courses:
                dico = dict()
                dico["course"] = course.name
                dico["department"] = department.name
                courses_depts.append(dico)

        return render_template("course/see_courses.html", total=courses_depts, dp=department)


@course.route('/upload_course_results', methods=['GET', 'POST'])
@login_required
def upload_course_results():
    le_semestre = ""
    le_cours = ""
    semesters = []
    the_semester = Semester.query.all()
    for semester in the_semester:
        semesters.append(semester)

    allcourses = [teach.course for teach in current_user.teaches.all()]

    if request.method == 'POST':
        val = request.form['course']
        sem = request.form['semester']
        students = []
        grades = []

        le_cours = Course.query.filter_by(id=int(val)).first()
        le_semestre = Semester.query.filter_by(id=sem).first()

        studentsenrolled = Enrollment.query.filter_by(course_id=int(val), semester_id=int(sem)).all()
        for student in studentsenrolled:
            students.append(User.query.filter_by(id=student.student_id).first())
            grades.append(student.grade)

        return render_template("course/upload_course_results.html",
                               allcourses=allcourses,
                               thecourse=le_cours,
                               students=students,
                               semesters=semesters,
                               le_semestre=le_semestre,
                               grades=grades)
    else:
        return render_template("course/upload_course_results.html", allcourses=allcourses,
                               le_semestre=le_semestre,
                               semesters=semesters,
                               thecourse=le_cours)


@course.route('/upload_course_results/<int:user_id>,<int:course_id>,<int:grade>,<int:semester_id>')
@login_required
@role_required(teacher=True, cd=True)
def save_grade(user_id, course_id, grade, semester_id):
    enrollment_instance = Enrollment.query.filter_by(student_id=user_id, course_id=course_id,
                                                     semester_id=semester_id).first()

    enrollment_instance.grade = grade
    db.session.add(enrollment_instance)
    db.session.commit()

    flash("Grade updated", FLASH_SUCCESS)
    return redirect(url_for("course.upload_course_results"))


@course.route('/contract/', methods=["GET"])
@course.route('/contract/<int:semester_id>', methods=["GET", "POST"])
@login_required
@role_required(student=True)
def contract(semester_id=None):
    # all the semesters for the default degree
    period = current_user.get_default_period()
    degree = period.degree
    semesters = User.get_semesters_for_period(period)

    if semester_id is None:  # use default semester
        semester = semesters[0]
    else:  # has semester from url
        semester = Semester.get_by_id(semester_id)

    has_contract = current_user.has_contract_signed(semester, degree)
    courses_enrolled = current_user.get_courses_enrolled_semester(semester, degree)

    return render_template("course/contract.html",
                           semesters=semesters,
                           has_contract=has_contract,
                           courses_enrolled=courses_enrolled,
                           selected_semester=semester)


@course.route('/establish_courses')
@login_required
@role_required(teacher=True, cd=True)
def establish_courses():
    return render_template("course/establish_courses.html")
