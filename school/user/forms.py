from flask_wtf import Form
from wtforms import PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from school.forms import RedirectForm
from flask.ext.login import current_user


class ChangePasswordForm(RedirectForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirmed_password = PasswordField('Confirm password',
                                       validators=[DataRequired(), EqualTo('new_password', "Confirm password is different from New password field")])
    submit = SubmitField('Update password')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def get_new_password(self):
        return self.new_password.data

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError("Password is wrong.")
