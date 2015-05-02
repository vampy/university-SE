from flask_wtf import Form
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask import flash
from school.config import FLASH_ERROR
from school.forms import RedirectForm
from flask.ext.login import current_user


class ChangePasswordForm(RedirectForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirmed_password = PasswordField('Confirm password', validators=[DataRequired()])
    update_password = SubmitField('Update password')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def get_new_password(self):
        return self.new_password.data

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if not current_user.verify_password(self.old_password.data):
            flash("Old password isn't valid", FLASH_ERROR)
            return False
        if self.new_password.data != self.confirmed_password.data:
            flash("Password doesn't match the confirmation", FLASH_ERROR)
            return False
        return True