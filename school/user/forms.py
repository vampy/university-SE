from flask_wtf import Form
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask import flash
from school.config import FLASH_ERROR
from school.forms import RedirectForm


class ChangePasswordForm(RedirectForm):
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirmed_password = PasswordField('Confirm password', validators=[DataRequired()])
    change = SubmitField('Change')

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