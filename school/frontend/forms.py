from wtforms import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email
from ..user import User
from flask import flash
from school.config import FLASH_ERROR
from school.forms import RedirectForm


class LoginForm(RedirectForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
    csrf_enabled = False

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


class PasswordResetForm(RedirectForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')
    csrf_enabled = False

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user is None:
            flash("Can't find that email, sorry.", FLASH_ERROR)
            return False
        self.user = user
        return True


class PasswordResetSubmitForm(RedirectForm):
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirmed_password = PasswordField('Confirm password',
                                       validators=[DataRequired(), EqualTo('new_password', "Confirm password is different from New password field")])
    submit = SubmitField('Change password')
    csrf_enabled = False
