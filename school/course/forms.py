from flask_wtf import Form
from wtforms import PasswordField, SubmitField, BooleanField, StringField, SelectField, TextAreaField
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

class CDEditCourseForm(TeacherAddCourseForm):
    category = SelectField("Category", coerce=int, validators=[DataRequired()],
                           choices=[(i, i) for i in range(2, 6)])
    approval_reason = TextAreaField("Reason")
    is_approved = BooleanField("Approved")

    submit = SubmitField("Edit Optional Course")
