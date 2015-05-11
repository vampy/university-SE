from wtforms import PasswordField, SubmitField, ValidationError, StringField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email
from school.forms import RedirectForm
from flask.ext.login import current_user


class AddCourse(RedirectForm):
    pass
