from flask.ext.login import login_required, current_user
from flask import Blueprint, render_template, flash, redirect, url_for, request
from school.decorators import role_required
from school.config import FLASH_SUCCESS, FLASH_ERROR
from school.models import *
from school.user import User
from .forms import TeacherAddCourseForm, CDEditCourseForm
from datetime import date

course = Blueprint('course', __name__)


@course.route('/see_courses', methods=['GET', 'POST'])
@course.route('/see_courses/<int:semester_id>', methods=['GET', 'POST'])
@login_required
def see_courses(semester_id=None):
    if current_user.is_student():

        period = current_user.get_default_period()
        degree = period.degree
        semesters = User.get_semesters_for_period(period)
        group = current_user.get_group(period)
        year, sem_nr = User.get_current_year_semester(semesters)

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
                               selected_semester=semester,
                               group=group,
                               degree=degree,
                               year=year,
                               semester_nr=sem_nr)
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
            if teach.course.is_approved:
                courses.append(teach.course)

        return render_template("course/see_courses.html", courses=courses)

    elif current_user.is_chief_department():

        department = current_user.get_department_cd()

        courses_depts = []
        for degree in department.degrees:
            for course in degree.courses:
                dico = dict()
                dico["course"] = course.name
                dico["department"] = department.name
                courses_depts.append(dico)

        courses = []
        for teach in current_user.teaches.all():
            if teach.course.is_approved:
                courses.append(teach.course)

        return render_template("course/see_courses.html", total=courses_depts, dp=department, courses=courses)


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

@course.route('/contract/start/<int:semester_id>')
@course.route('/contract/action/<int:semester_id>/<int:add>/<int:course_id>')
@login_required
@role_required(student=True)
def contract_action(semester_id, add=None, course_id=None):
    # get info from database
    semester = Semester.get_by_id(semester_id)
    period = current_user.get_default_period()
    degree = period.degree
    has_contract = current_user.has_contract_signed(semester, degree)
    courses_enrolled = current_user.get_courses_enrolled_semester(semester, degree)
    return_path = redirect(url_for('course.contract', semester_id=semester_id))

    # validate
    if has_contract:
        flash("Your contract is already signed for that semester", FLASH_ERROR)
        return return_path

    # start contract
    if add is None and course_id is None:
        if courses_enrolled:
            flash("You already started the temporary contract for that semester", FLASH_ERROR)
            return return_path

        # add initial obligatory courses
        obligatory_courses = semester.filter_obligatory_courses(degree)
        for c in obligatory_courses:
            db.session.add(Enrollment(student=current_user, semester=semester, course=c))
        db.session.commit()

        flash("Added obligatory courses", FLASH_SUCCESS)
        return return_path

    # add or remove course from contract
    course_add = Course.get_by_id(course_id)
    if not course_add.is_optional:
        flash("Course is not optional", FLASH_ERROR)
        return return_path

    courses = [x[1] for x in courses_enrolled]
    if add:  # add course
        if course_add in courses:  # validate
            flash("You are already enrolled for that course", FLASH_ERROR)
            return return_path

        db.session.add(Enrollment(student=current_user, semester=semester, course=course_add))
        db.session.commit()

        flash("Course Added", FLASH_SUCCESS)
    else:
        if course_add not in courses:   # validate
            flash("You are not enrolled for that course", FLASH_ERROR)
            return return_path

        db.session.delete(Enrollment.query.filter_by(student=current_user, semester=semester, course=course_add).first())
        db.session.commit()

        flash("Course Removed", FLASH_SUCCESS)

    return return_path

@course.route('/contract/', methods=["GET"])
@course.route('/contract/<int:semester_id>', methods=["GET", "POST"])
@login_required
@role_required(student=True)
def contract(semester_id=None):
    # all the semesters for the default degree
    period = current_user.get_default_period()
    degree = period.degree
    group = current_user.get_group(period)
    semesters = User.get_semesters_for_period(period)
    year, sem_nr = User.get_current_year_semester(semesters)

    if semester_id is None:  # use default semester
        semester = semesters[0]
    else:  # has semester from url
        semester = Semester.get_by_id(semester_id)

    has_contract = current_user.has_contract_signed(semester, degree)
    courses_enrolled = current_user.get_courses_enrolled_semester(semester, degree)

    # get optional courses
    courses_contract = []
    if not has_contract:
        courses_contract = semester.filter_courses(degree)

        # auto build check to see if optional course is already in the contract
        courses_enrolled_first = [x[1] for x in courses_enrolled]
        for i, c in enumerate(courses_contract):
            courses_contract[i].is_in_contract = False
            if c in courses_enrolled_first:
                courses_contract[i].is_in_contract = True

    return render_template("course/contract.html",
                           semesters=semesters,
                           semester_sel=semester,
                           semester_nr=sem_nr,
                           year=year,
                           group=group,
                           degree=degree,
                           has_contract=has_contract,
                           courses_enrolled=courses_enrolled,
                           courses_contract=courses_contract)

@course.route('/remove_optional_course/<int:course_id>', methods=["GET"])
@login_required
@role_required(teacher=True, cd=True)
def remove_optional_course(course_id):  # TODO check if secure
    found_course = Course.get_by_id(course_id)
    year = date.today().year
    return_path = redirect(url_for("course.establish_courses"))

    if current_user.is_teacher():
        optional_teaches = Teaches.get_optional_courses_teacher(current_user, year)
        for teaches in optional_teaches:
            if found_course.id == teaches.course.id:  # found course remove it
                # update database
                db.session.delete(found_course)
                db.session.delete(teaches)
                db.session.commit()

                flash("Removed optional course", FLASH_SUCCESS)
                return return_path

        flash("Can not remove that optional course", FLASH_ERROR)
        return return_path

    flash("TODO", FLASH_ERROR)
    return return_path

@course.route('/edit_optional_course/<int:course_id>', methods=["GET", "POST"])
@login_required
@role_required(cd=True)
def edit_optional_course(course_id):
    found_course = Course.get_by_id(course_id)
    department = current_user.get_department_cd()
    return_path = redirect(url_for('course.establish_courses'))

    if not found_course.is_optional:
        flash("This course is not optional", FLASH_ERROR)
        return return_path

    # degree not in department, can not edit
    if found_course.degree not in department.degrees:
        flash("You can not edit that course because it is not in your department", FLASH_ERROR)
        return return_path

    # if done properly, an optional course will appear only once in the teaches table
    teaches = Teaches.query.filter_by(course=found_course).first()
    if teaches is None:
        flash("Optional Course is not proposed by anyone", FLASH_ERROR)
        return return_path

    semesters = Semester.get_semesters_year(date.today().year)
    if teaches.semester not in semesters:
        flash("You can not longer edit this optional course. The time has passed.", FLASH_ERROR)
        return return_path

    # build form
    form = CDEditCourseForm()
    if not form.is_submitted():  # set name, degree_id, category, reason, is_approved
        form = CDEditCourseForm(obj=found_course)

    form.semester_id.choices = [(s.id, s.name) for s in semesters]
    form.degree_id.choices = [(d.id, d.name) for d in department.degrees]

    if form.validate_on_submit():
        form_approve = bool(form.is_approved.data)
        form_semester = form.semester_id.data

        # find semester
        semester = None
        for s in semesters:
            if form_semester == s.id:
                semester = s

        if semester is None:  # check for impossible condition
            return "this should never happen, semester is none"

        if found_course.is_approved is True and form_approve is False:  # set not approved
            teaches.semester_id = form.semester_id.data
            # remove from semester_courses
            found_course.semesters = []

        elif found_course.is_approved is False and form_approve is True:  # approve course
            teaches.semester_id = form_semester
            # add to semester_courses
            found_course.semesters.append(semester)

        # set name, degree_id, category, reason, is_approved
        form.populate_obj(found_course)
        found_course.is_approved = form_approve
        teaches.semester = semester

        # update db
        db.session.add_all([found_course, teaches])
        db.session.commit()

        flash("Course Updated", FLASH_SUCCESS)
    else:
        form.semester_id.data = teaches.semester.id  # set semester id

    return render_template("course/edit_optional_course.html",
                           course=found_course,
                           teaches=teaches,
                           form=form)


@course.route('/establish_courses', methods=["GET", "POST"])
@login_required
@role_required(teacher=True, cd=True)
def establish_courses():
    year = date.today().year

    if current_user.is_teacher():  # teacher
        if not current_user.is_lecturer():
            flash("You are not a lecturer, so you can't add optional courses", FLASH_ERROR)
            return redirect(url_for("user.index"))

        semesters = Semester.get_semesters_year(year)
        department = current_user.get_department_teacher()
        degrees = department.degrees
        optional_teaches = Teaches.get_optional_courses_teacher(current_user, year)
        can_add = (len(optional_teaches) < 2)  # only 2 optional course per year

        # build form
        add_form = TeacherAddCourseForm()
        if can_add:
            add_form.semester_id.choices = [(s.id, s.name) for s in semesters]
            add_form.degree_id.choices = [(d.id, d.name) for d in degrees]
            if add_form.validate_on_submit():
                # add optional course to database
                current_user.add_optional_course(add_form.name.data, add_form.degree_id.data, add_form.semester_id.data)

                # update view
                flash("Optional course added", FLASH_SUCCESS)
                add_form.name.data = ""
                optional_teaches = Teaches.get_optional_courses_teacher(current_user, year)
                can_add = (len(optional_teaches) < 2)

        return render_template("course/establish_courses.html",
                               add_form=add_form,
                               can_add=can_add,
                               optional_teaches=optional_teaches)

    # cd
    department = current_user.get_department_cd()
    optional_teaches = Teaches.get_optional_courses_department(department, year)

    return render_template("course/establish_courses.html", optional_teaches=optional_teaches)
