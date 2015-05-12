from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask.ext.login import login_required, logout_user, current_user, login_user
from .forms import LoginForm, PasswordResetForm, PasswordResetSubmitForm
from school.config import FLASH_SUCCESS, FLASH_INFO, FLASH_WARNING
from school.user.models import User
from os import urandom
from school.extensions import *
from flask.ext.mail import Mail, Message



frontend = Blueprint('frontend', __name__)


@frontend.route('/login', methods=["GET", "POST"])
def login():

    if current_user.is_authenticated():  # user is already logged in
        flash("You are already logged in", FLASH_WARNING)
        return redirect(url_for('user.index'))

    form = LoginForm()

    if form.validate_on_submit():
        if form.remember_me.data:
            flash("Remember me checked.", FLASH_INFO)
            login_user(form.user, remember=True)
        else:
            login_user(form.user)

        return form.redirect("user.index")

    return render_template('frontend/index.html', form=form)


@frontend.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', FLASH_INFO)

    return redirect(url_for("frontend.login"))


@frontend.route('/password_reset', methods=["GET", "POST"])
def password_reset():
    token = request.args.get('token', None)
    flash(token, FLASH_INFO)
    if not token:
        form = PasswordResetForm(request.form)
        if form.validate_on_submit():
            email = form.email.data
            user = User.query.filter_by(email=email).first()
            if user:
                token = user.get_token()
                flash(token, FLASH_INFO)
                print(token)
            return form.redirect("frontend.login")
        return render_template('frontend/password_reset.html', form=form)
    verified_result = User.verify_token(token)
    if token and verified_result:
        is_verified_token = True
        password_submit_form = PasswordResetSubmitForm(request.form)
        if password_submit_form.validate_on_submit():
            verified_result.password = password_submit_form.new_password.data
            verified_result.is_active = True
            db.session.add(verified_result)
            db.session.commit()
            #return "password updated successfully"
            flash("password updated successfully")
            return password_submit_form.redirect("user.index")


# def password_reset_submit():
#     token = request.args.get()
#     verified_result = User.verify_token(token)
#     if token and verified_result:
#     is_verified_token = True
#     password_submit_form = PasswordResetSubmitForm(request.form)
#     if password_submit_form.validate_on_submit():
#         verified_result.password = generate_password_hash(password_submit_form.password.data)
#         verified_result.is_active = True
#         db.session.add(verified_result)
#         db.session.commit()
#         #return "password updated successfully"
#         flash("password updated successfully")
#         return redirect(url_for('users.login_view'))

