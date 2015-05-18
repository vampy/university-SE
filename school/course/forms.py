from flask_wtf import Form
from wtforms import PasswordField, SubmitField, ValidationError, StringField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email
from school.forms import RedirectForm
from flask.ext.login import current_user

class EditCourseForm(Form):
    pass

class AddCourseForm(Form):
    pass


class TeacherAddCourseForm(Form):
    name = StringField("Name", validators=[DataRequired()])
    degree_id = SelectField("Degree", coerce=int, validators=[DataRequired()], choices=[])
    semester_id = SelectField("Semester", coerce=int, validators=[DataRequired()], choices=[])

    submit = SubmitField("Add Optional Course")
