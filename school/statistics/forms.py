from flask_wtf import Form
from wtforms import SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, NumberRange
from school.user import User
from school.user.models import Role


class Statistic:
    ORDERED_STUDENTS = 0
    TEACHER_RANKING = 1
    TEACHER_DISCIPLINES = 2


class SelectStatisticForm(Form):
    selected_statistic = SelectField(label="Available statistics", coerce=int,
                                     choices=[(Statistic.ORDERED_STUDENTS, "Students ordered by their professional results."),
                                              (Statistic.TEACHER_RANKING, "Teacher with the best/worst results obtained."),
                                              (Statistic.TEACHER_DISCIPLINES, "Disciplines given by a teacher")])
    submit = SubmitField("Choose")


class OrderedStudentsStatisticFrom(Form):
    presentation = "Ordered students"
    from_each = SelectField(label="From each", coerce=int,
                            choices=[(0, "Group"), (1, "Year")])

    order = SelectField(label="Order by", coerce=int,
                        choices=[(0, "Average mark (descending)"), (1, "Name (alphabetically)")])

    message = "Value should be in the interval [%(min)s,%(max)s]."
    average_mark_lower_bound = DecimalField(label="Lower bound",
                                            default=1,
                                            validators=[DataRequired(), NumberRange(min=1, max=10, message=message)])

    average_mark_upper_bound = DecimalField(label="Upper bound", default=10)
    show_statistic = SubmitField("Show")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        message = "Value should be in the interval [%(min)s,%(max)s]."
        self.average_mark_upper_bound.validators = [DataRequired(), NumberRange(min=self.average_mark_lower_bound.data,
                                                                                max=10,
                                                                                message=message)]


class TeacherDisciplinesStatisticForm(Form):
    presentation = "Disciplines given by a teacher"
    teacher_name = SelectField(label="Teacher", coerce=int)
    submit = SubmitField("Show")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_name.choices = [(t.id, t.realname) for t in
                                     User.query.filter_by(role_id=Role.TEACHER).order_by('realname')]


# Teacher With Best Or Worst Results Obtained
class TeacherWBOWROStatisticForm(Form):
    presentation = "Teacher with best or worst results obtained"
    criteria = SelectField(label="Criteria", coerce=int,
                           choices=[(0, "Best results obtained"), (1, "Worst results obtained")])
    submit = SubmitField("Show")
