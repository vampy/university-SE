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


# TODO
def settings():
    pass

