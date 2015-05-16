from flask import Blueprint, render_template, url_for, redirect, flash, request, current_app
from flask.ext.login import login_required, logout_user, current_user, login_user
from .forms import LoginForm, PasswordResetForm, PasswordResetSubmitForm
from school.config import FLASH_SUCCESS, FLASH_INFO, FLASH_WARNING, FLASH_ERROR
from school.user.models import User
from school.extensions import *
from flask.ext.mail import Message

frontend = Blueprint('frontend', __name__)


@frontend.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated():  # user is already logged in
        flash("You are already logged in", FLASH_WARNING)
        return redirect(url_for('user.index'))

    form = LoginForm()
    if form.validate_on_submit():
        if form.remember_me.data:
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
    token = request.args.get('token')

    # display password request form
    if token is None:
        password_reset_form = PasswordResetForm()
        if password_reset_form.validate_on_submit():
            email = password_reset_form.email.data
            user = password_reset_form.user
            if user is not None:

                # user has already a token present
                if User.verify_token(user.active_token):
                    flash("This email has a active reset password link still active. Please check your email spam folder.", FLASH_ERROR)
                    return render_template('frontend/password_reset.html', form=password_reset_form)

                # generate new token
                token = user.get_token()
                user.active_token = token
                db.session.add(user)
                db.session.commit()

                # send mail
                msg = Message('Reset password', sender='academicinfo.seproject@gmail.com', recipients=[email])
                msg.html = render_template('emails/password_reset_email.html', user=user, token=token)
                mail.send(msg)

                return render_template('frontend/password_reset_confirmation_sent.html')
        return render_template('frontend/password_reset.html', form=password_reset_form)

    # a token was given
    verified_result = User.verify_token(token)

    # given token is not valid
    if verified_result is None or verified_result.active_token is None:
        flash("It looks like you clicked on an invalid password reset link. Please try again.", FLASH_ERROR)
        password_reset_form = PasswordResetForm()
        return render_template('frontend/password_reset.html', form=password_reset_form)

    # the token is good
    password_submit_form = PasswordResetSubmitForm()
    if password_submit_form.validate_on_submit():
        # we make sure that the token is used only once
        verified_result.password = password_submit_form.new_password.data
        verified_result.active_token = None
        db.session.add(verified_result)
        db.session.commit()

        # send mail
        msg = Message('Your password has changed',
                      sender='academicinfo.seproject@gmail.com', recipients=[verified_result.email])
        msg.html = render_template('emails/changed_password_email.html', user=verified_result)
        mail.send(msg)

        flash("New password set successfully.", FLASH_SUCCESS)
        return redirect(url_for("frontend.login"))

    return render_template('frontend/password_reset_submit.html', token=token,
                           password_submit_form=password_submit_form)
