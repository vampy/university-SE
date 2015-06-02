from flask.ext.login import login_required, current_user
from flask import Blueprint, render_template, flash, redirect, url_for, request
from school.decorators import role_required
from school.config import FLASH_SUCCESS, FLASH_ERROR
from school.models import *
from school.user import User
from school.util import is_integer
from .forms import TeacherAddCourseForm, CDEditCourseForm

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
                    courses_depts.append({
                        "course": course.name,
                        "department": department.name
                    })

        return render_template("course/see_courses.html", total=courses_depts, depts=depts)

    elif current_user.is_teacher():
        # TODO group by semester
        courses = [teach.course for teach in current_user.teaches.all() if teach.course.is_approved]

        return render_template("course/see_courses.html", courses=courses)

    elif current_user.is_chief_department():
        department = current_user.get_department_cd()

        courses_depts = []
        for degree in department.degrees:
            for course in degree.courses:
                courses_depts.append({
                    "course": course.name,
                    "department": department.name
                })

        courses = [teach.course for teach in current_user.teaches.all() if teach.course.is_approved]

        return render_template("course/see_courses.html", total=courses_depts, dp=department, courses=courses)


@course.route('/upload_course_results/<int:course_id>/<int:semester_id>', methods=['GET', 'POST'])
@course.route('/upload_course_results/<int:course_id>/', methods=['GET', 'POST'])
@login_required
@role_required(teacher=True, cd=True)
def upload_course_results(course_id, semester_id=None):
    selected_course = Course.get_by_id(course_id)

    # form submitted, redirect
    if request.method == 'POST':
        # validate
        if 'semester_id' not in request.form:
            flash("upload_course_results semester_id is missing", FLASH_ERROR)
            return redirect(url_for('course.see_courses'))
        if not is_integer(request.form['semester_id']):
            flash("upload_course_results semester_id is not an integer", FLASH_ERROR)
            return redirect(url_for('course.see_courses'))

        return redirect(url_for('course.upload_course_results',
                                course_id=selected_course.id,
                                semester_id=int(request.form['semester_id'])))

    # display students and grades
    if semester_id is not None:
        selected_semester = Semester.get_by_id(semester_id)
        students_enrolled = Enrollment.query.filter_by(course_id=course_id, semester_id=semester_id).all()

        seen_groups = set()
        groups = []
        for se in students_enrolled:
            g = se.student.get_group(se.student.get_default_period())
            if g not in seen_groups:
                seen_groups.add(g)
                groups.append(g)

        return render_template("course/upload_course_results.html",
                               students_enrolled=students_enrolled,
                               semesters=selected_course.semesters,
                               selected_course=selected_course,
                               selected_semester=selected_semester,
                               groups=groups, )

    # use default to be first semester
    if not selected_course.semesters:
        flash("Selected course does not have any semesters", FLASH_ERROR)
        return redirect(url_for('course.see_courses'))

    return redirect(url_for('course.upload_course_results',
                            course_id=selected_course.id,
                            semester_id=selected_course.semesters[0].id))


@course.route('/save_grade/<int:course_id>/<int:semester_id>', methods=['POST'])
@login_required
@role_required(teacher=True, cd=True)
def save_grade(course_id, semester_id):

    # TODO validate
    selected_semester = Semester.get_by_id(semester_id)
    selected_course = Course.get_by_id(course_id)
    return_path = redirect(
        url_for('course.upload_course_results', course_id=selected_course.id, semester_id=selected_semester.id))

    students_enrolled = Enrollment.query.filter_by(course_id=course_id, semester_id=semester_id).all()
    for enrolled in students_enrolled:

        if str(enrolled.student_id) not in request.form:
            flash("save_grade missing argument", FLASH_ERROR)
            return return_path

        if request.form[str(enrolled.student_id)].isnumeric():
            grade = int(request.form[str(enrolled.student_id)])
            if 0 <= grade <= 10:  # save new grade
                enrolled.grade = grade
                db.session.add(enrolled)
                db.session.commit()
            else:
                flash("A grade should be between 0 and 10", FLASH_ERROR)
                return return_path
        else:
            flash("A grade should be numeric", FLASH_ERROR)
            return return_path

    flash("Grade updated", FLASH_SUCCESS)
    return return_path


@course.route('/contract/start/<int:semester_id>')
@course.route('/contract/action/<int:semester_id>/<int:action>/<int:course_id>', methods=['GET', 'POST'])
@login_required
@role_required(student=True)
def contract_action(semester_id, action=None, course_id=None):
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
    if action is None and course_id is None:
        if courses_enrolled:
            flash("You already started the temporary contract for that semester", FLASH_ERROR)
            return return_path

        # add initial obligatory courses
        obligatory_courses = semester.filter_obligatory_courses(degree)
        courses_all = [c for e, c in current_user.get_courses_enrolled(degree)]
        for c in obligatory_courses:
            # exists = Enrollment.query.filter_by(student=current_user, course=c).first()
            if c not in courses_all:  # only add course from current year
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
    if action == 1:  # add course
        if course_add in courses:  # validate
            flash("You are already enrolled for that course", FLASH_ERROR)
            return return_path

        db.session.add(Enrollment(student=current_user, semester=semester, course=course_add, priority=1))
        db.session.commit()

        flash("Course Added", FLASH_SUCCESS)
    elif action == 2:  # remove course
        if course_add not in courses:  # validate
            flash("You are not enrolled in that course", FLASH_ERROR)
            return return_path

        db.session.delete(
            Enrollment.query.filter_by(student=current_user, semester=semester, course=course_add).first())
        db.session.commit()

        flash("Course Removed", FLASH_SUCCESS)
    elif action == 3:  # set course priority
        if course_add not in courses:  # validate
            flash("You are not enrolled in that course", FLASH_ERROR)
            return return_path
        if request.method != 'POST':
            flash("You did not submit any form", FLASH_ERROR)
            return return_path
        if "priority" not in request.form:
            flash("Priority value is missing", FLASH_ERROR)
            return return_path
        if not is_integer(request.form["priority"]):
            flash("Please input a valid integer for the priority", FLASH_ERROR)
            return return_path

        priority = int(request.form["priority"])
        if priority < 2 or priority > 9:
            flash("Priority value is invalid. Should be between 2 and 9", FLASH_ERROR)
            return return_path

        enroll = Enrollment.query.filter_by(student=current_user, semester=semester, course=course_add).first()
        enroll.priority = priority
        db.session.add(enroll)
        db.session.commit()

        flash("Priority set", FLASH_SUCCESS)
    else:
        flash("Action is wrong", FLASH_ERROR)

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
    courses_semester = []
    packages = {}  # map from package to set of priorities
    if not has_contract:
        courses_semester = semester.filter_courses(degree)

        # add to seen packages
        for enrolled, c in courses_enrolled:
            if c.package not in packages:
                packages[c.package] = set()

            packages[c.package].add(c.id)

        # auto build check to see if optional course is already in the contract
        courses_enrolled_first = [c for e, c in courses_enrolled]
        courses_enrolled_all = [c for e, c in current_user.get_courses_enrolled(degree)]
        remove_list = []
        for i, c in enumerate(courses_semester):
            # remove from courses_semester if we already seen that course
            if c in courses_enrolled_all:
                remove_list.append(c)

            courses_semester[i].is_in_contract = False
            if c in courses_enrolled_first:
                courses_semester[i].is_in_contract = True

        # remove courses not of this semester
        for c in remove_list:
            courses_semester.remove(c)

    return render_template("course/contract.html",
                           semesters=semesters,
                           semester_sel=semester,
                           semester_nr=sem_nr,
                           year=year,
                           group=group,
                           degree=degree,
                           has_contract=has_contract,
                           courses_enrolled=courses_enrolled,
                           courses_semester=courses_semester,
                           packages=packages)


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
    if not form.is_submitted():  # set name, degree_id, type_id, reason, is_approved
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
                break

        if semester is None:  # check for impossible condition
            return "this should never happen, semester is none"

        if found_course.is_approved is True and form_approve is False:  # set not approved
            # remove from semester_courses
            found_course.semesters = []

        # approve course
        elif (found_course.is_approved is False and form_approve is True) \
                or semester != teaches.semester:  # semesters differ
            # add to semester_courses
            found_course.semesters = [semester]

        # set name, degree_id, type_id, reason, is_approved
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
