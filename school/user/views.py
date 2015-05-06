from flask.ext.login import login_required, current_user
from flask import Blueprint, render_template, flash, redirect, url_for, request
from .forms import ChangePasswordForm, EditUserForm, AddUserForm
from .models import User
from school.config import FLASH_SUCCESS, FLASH_ERROR
from school.decorators import role_required
from school.models import *

user = Blueprint('user', __name__)


# the root of our website
@user.route('/')
@login_required
def index():
    return render_template("user/index.html")


@user.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        flash('Password changed successfully.', FLASH_SUCCESS)
        current_user.password = form.new_password.data

        db.session.add(current_user)
        db.session.commit()

        return form.redirect("user.index")

    return render_template('user/changepassword.html', form=form)



@user.route('/see_courses', methods=['GET', 'POST'])
@login_required
def see_courses():
    if current_user.is_student():

        seen_semesters = set()
        semesters = []
        for enroll in current_user.enrolled.all():
            if enroll.semester not in seen_semesters:
                semesters.append(enroll.semester)
                seen_semesters.add(enroll.semester)

        if request.method == 'POST':
            if request.form['semester'] == '0':
                flash("Please choose a semester", FLASH_ERROR)
                return render_template("user/see_courses.html", semesters=semesters)
            else:
                courses = []
                grades = []
                sem_id = request.form['semester']
                for enroll in current_user.enrolled.all():
                    if enroll.semester.id == int(sem_id):
                        courses.append(enroll.course)
                        grades.append(enroll.grade)

        else:
            courses = []
            grades = []
        #grades = [enroll.grade for enroll in current_user.enrolled.all()]
        #courses = [enroll.course for enroll in current_user.enrolled.all()]

        return render_template("user/see_courses.html", semesters=semesters, grades=grades, courses=courses)
    elif current_user.is_admin():
        courses = Course.query.order_by("name").all()
        return render_template("user/see_courses.html", courses=courses)

    elif current_user.is_teacher():
        courses = Course.query.all()
        return render_template("user/see_courses.html", courses=courses)

    elif current_user.is_chief_department():
        courses = Course.query.all()
        return render_template("user/see_courses.html", courses=courses)


@user.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required(admin=True, cd=True)
def profile(user_id):
    user_instance = User.get_by_id(user_id)
    form = EditUserForm(obj=user_instance)
    if form.validate_on_submit():
        flash("Updated user details", FLASH_SUCCESS)

        form.populate_obj(user_instance)

        db.session.add(user_instance)
        db.session.commit()

    return render_template("user/user.html", user=user_instance, form=form)


@user.route('/user/delete/<int:user_id>')
@login_required
@role_required(admin=True, cd=True)
def delete(user_id):
    user_instance = User.get_by_id(user_id)
    if user_instance.id == current_user.id:
        flash("You can not delete yourself ;)", FLASH_ERROR)
        return redirect(url_for("user.users"))

    flash("User %s deleted" % user_instance.username, FLASH_SUCCESS)

    db.session.delete(user_instance)
    db.session.commit()

    return redirect(url_for("user.users"))


@user.route('/users', methods=['GET', 'POST'])
@login_required
@role_required(admin=True, cd=True)
def users():
    # CD can edit users only in this department

    form = AddUserForm()
    if form.validate_on_submit():  # add user

        # update database
        user_instance = User()
        form.populate_obj(user_instance)
        db.session.add(user_instance)
        db.session.commit()

        # update view
        form = AddUserForm()
        flash("User added", FLASH_SUCCESS)

    users_list = User.query.all()
    return render_template("user/users.html", users=users_list, add_form=form)



@user.route('/upload_course_results', methods=['GET', 'POST'])
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
        val=request.form['course']
        sem=request.form['semester']
        students = []
        grades = []

        le_cours = Course.query.filter_by(id=int(val)).first()
        le_semestre = Semester.query.filter_by(id=sem).first()

        studentsenrolled = Enrollment.query.filter_by(course_id=int(val),semester_id=int(sem)).all()
        for student in studentsenrolled:
            students.append(User.query.filter_by(id=student.student_id).first())
            grades.append(student.grade)

        return render_template("user/upload_course_results.html",
                               allcourses=allcourses,
                               thecourse=le_cours,
                               students=students,
                               semesters=semesters,
                               le_semestre=le_semestre,
                               grades=grades)
    else :
        return render_template("user/upload_course_results.html",allcourses=allcourses,
                               le_semestre=le_semestre,
                               semesters=semesters,
                               thecourse=le_cours)


@user.route('/upload_course_results/<int:user_id>,<int:course_id>,<int:grade>,<int:semester_id>')
@login_required
@role_required(teacher=True, cd=True)
def save_grade(user_id,course_id,grade,semester_id):
    enrollment_instance = Enrollment.query.filter_by(student_id=user_id,course_id=course_id,semester_id=semester_id).first()

    enrollment_instance.grade=grade
    db.session.add(enrollment_instance)
    db.session.commit()

    flash("Grade updated", FLASH_SUCCESS)
    return redirect(url_for("user.upload_course_results"))

# TODO
def settings():
    pass

