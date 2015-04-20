from flask import Blueprint, render_template, url_for, redirect, flash
from flask.ext.login import login_required, logout_user, current_user, login_user
from .forms import LoginForm
from school.config import FLASH_SUCCESS, FLASH_INFO

frontend = Blueprint('frontend', __name__)


@frontend.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated():  # user is already logged in
        return redirect(url_for('user.index'))

    form = LoginForm()
    if form.validate_on_submit():
        flash(u'Successfully logged in as %s' % form.user.username, FLASH_SUCCESS)
        login_user(form.user)

        return form.redirect("user.index")

    return render_template('frontend/index.html', form=form)


@frontend.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', FLASH_INFO)

    return redirect(url_for("frontend.login"))
