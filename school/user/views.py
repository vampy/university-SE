from flask.ext.login import login_required, current_user
from flask import Blueprint, render_template, flash, redirect, url_for, request
from .forms import ChangePasswordForm, EditUserForm, AddUserForm
from .models import User
from school.config import FLASH_SUCCESS, FLASH_ERROR
from school.decorators import role_required
from school.extensions import db, mail
from flask_mail import Message

user = Blueprint('user', __name__)

# the root of our website
@user.route('/')
@login_required
def index():
    return render_template("user/index.html")


@user.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        flash('Password changed successfully.', FLASH_SUCCESS)
        current_user.password = form.new_password.data

        db.session.add(current_user)
        db.session.commit()

        msg = Message('Your password has changed', sender='academicinfo.seproject@gmail.com', recipients=[current_user.email])
        msg.html = render_template('emails/changed_password_email.html', user=current_user)
        mail.send(msg)
        return form.redirect("user.index")

    return render_template('user/change_password.html', form=form)


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
