from flask import Blueprint, render_template, flash, g
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

@user.route('/users')
@login_required  # TODO add admin_required
def users():
    return render_template("user/users.html")

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

