from flask import Blueprint, render_template, flash
from flask.ext.login import login_required, logout_user, current_user, login_user
from .forms import ChangePasswordForm
from school.config import FLASH_SUCCESS

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
    if form.validate():

        flash('Password changed successfully.', FLASH_SUCCESS)
        # TODO controller.changepassword(current_user,form.get_new_password)
        return form.redirect("user.index")

    return render_template('user/changepassword.html', form=form)


@user.route('/seeCourses')
@login_required
def seeCourses():
    courses = [
                {
                    'name': 'Operating system'
                },
                {
                    'name': 'Software design'
                },
                {
                    'name': 'Software engineering'
                },
                {
                    'name': 'Software quality'
                }
        ]

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

    return render_template("user/see_courses.html",courses=courses, projects=projects)

# TODO
def settings():
    pass

