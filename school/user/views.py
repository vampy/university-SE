from flask import Blueprint, render_template, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from .forms import ChangePasswordForm, EditUserForm
from school.extensions import db
from school.config import FLASH_SUCCESS, FLASH_ERROR
from school.decorators import role_required
from .models import User

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


@user.route('/see_courses')
@login_required
def see_courses():

    projects = [
        {
            'name': 'Test 1',
            'deadline': '2015-03-20',
            'grade': '10'
        },
        {
            'name': 'Project 1',
            'deadline': '2015-03-27',
            'grade': '9'
        },
        {
            'name': 'Exam mid term',
            'deadline': '2015-04-10',
            'grade': '8'
        },
        {
            'name': 'Project 2',
            'deadline': '2015-05-10',
            'grade': '10'
        }
    ]

    courses = [enroll.course for enroll in current_user.enrolled.all()]

    return render_template("user/see_courses.html", courses=courses, projects=projects)


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


@user.route('/users')
@login_required
@role_required(admin=True, cd=True)
def users():
    # CD can edit users only in this department

    users_list = User.query.all()
    return render_template("user/users.html", users=users_list)


@user.route('/uploadresults')
@login_required
def uploadresults():
    courses = [
                {
                    'name': 'Operating system',
                    'grade': '9'
                },
                {
                    'name': 'Software design',
                    'grade': '7'
                },
                {
                    'name': 'Software engineering',
                    'grade': '9'
                },
                {
                    'name': 'Software quality',
                    'grade': '8'
                }
        ]
    return render_template("user/upload_course_results.html", courses=courses)


# TODO
def settings():
    pass

