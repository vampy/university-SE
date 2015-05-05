from flask_wtf import Form
from wtforms import PasswordField, SubmitField, ValidationError, StringField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email
from school.forms import RedirectForm
from flask.ext.login import current_user
from .models import Role


class ChangePasswordForm(RedirectForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirmed_password = PasswordField('Confirm password',
                                       validators=[DataRequired(), EqualTo('new_password', "Confirm password is different from New password field")])
    submit = SubmitField('Update password')

    def get_new_password(self):
        return self.new_password.data

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError("Password is wrong.")


class EditUserForm(RedirectForm):
    username = StringField("Username", validators=[DataRequired()])
    realname = StringField("Real name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    role_id = SelectField("Role", coerce=int, validators=[DataRequired()],
                          choices=[(Role.STUDENT, "Student"), (Role.TEACHER, "Teacher"),
                                   (Role.CHIEF_DEPARTMENT, "ChiefDepartment"), (Role.ADMIN, "Admin")])

    submit = SubmitField("Update user")
