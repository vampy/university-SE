from flask_wtf import Form
from wtforms import SubmitField, BooleanField, StringField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp, NumberRange


class EditCourseForm(Form):
    pass


class AddCourseForm(Form):
    pass


class TeacherAddCourseForm(Form):
    name = StringField("Name", validators=[DataRequired(), Length(min=4, max=64), Regexp(r'^[a-zA-Z0-9 ]+$')])
    degree_id = SelectField("Degree", coerce=int, validators=[DataRequired()], choices=[])
    semester_id = SelectField("Semester", coerce=int, validators=[DataRequired()], choices=[])

    submit = SubmitField("Add Optional Course")


class CDEditCourseForm(TeacherAddCourseForm):
    category = SelectField("Category", coerce=int, validators=[DataRequired()],
                           choices=[(i, i) for i in range(2, 6)])
    min_students = IntegerField("Min Students", validators=[DataRequired()])
    max_students = IntegerField("Max Students", validators=[DataRequired()])
    credits = IntegerField("Credits", validators=[DataRequired(), NumberRange(min=1, max=10)])
    approval_reason = TextAreaField("Reason")
    is_approved = BooleanField("Approved")

    submit = SubmitField("Edit Optional Course")
