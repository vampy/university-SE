from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from ..user import User
from flask import flash
from school.config import FLASH_ERROR, FLASH_INFO
from school.forms import RedirectForm


class LoginForm(RedirectForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')  # TODO
    submit = SubmitField('Login')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    # custom validation, try validate user credentials
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user is None:
            flash("Invalid user/password", FLASH_ERROR)
            return False

        if not user.verify_password(self.password.data):
            flash("Invalid user/password", FLASH_ERROR)
            return False

        self.user = user
        return True


class ChangePasswordForm(RedirectForm):
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirmed_password = PasswordField('Confirm password', validators=[DataRequired()])
    change =SubmitField('Change');

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def get_new_password(self):
        return self.new_password.data

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.new_password.data != self.confirmed_password.data:
            flash("Password must be the same", FLASH_ERROR)
            return False
        return True




