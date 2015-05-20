from flask_wtf import Form
from wtforms import SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, NumberRange
from school.user import User
from school.user.models import Role


class SelectStatisticForm(Form):
    selected_statistic = SelectField(label="Available statistics", coerce=int,
                                     choices=[(0, "Students ordered by their professional results."),
                                              (1, "Teacher with the best/worst results obtained."),
                                              (2, "Disciplines given by a teacher")])
    submit = SubmitField("Choose")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self):
        rv = super().validate()
        if not rv:
            return False
        return True


class OrderedStudentsStatisticFrom(Form):
    presentation = "Ordered students"
    from_each = SelectField(label="From each", coerce=int,
                            choices=[(0, "Group"),
                                     (1, "Year")])

    order = SelectField(label="Order by", coerce=int,
                        choices=[(0, "Average mark (descending)"),
                                 (1, "Name (alphabetically)")])

    average_mark_lower_bound = DecimalField(label="Lower bound", default=1,
                                            validators=[DataRequired(),
                                                        NumberRange(min=1, max=10,
                                                        message="Value should be in the interval [%(min)s,%(max)s].")])

    average_mark_upper_bound = DecimalField(label="Upper bound", default=10)
    show_statistic = SubmitField("Show")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.average_mark_upper_bound.validators = [DataRequired(),
                                                    NumberRange(min=self.average_mark_lower_bound.data, max=10,
                                                                message="Value should be in the interval [%(min)s,%(max)s].")]

    def validate(self):
        rv = super().validate()
        if not rv:
            return False
        return True


#     Teacher With Best Or Worst Results Obtained
class TeacherWBOWROStatisticForm(Form):
    presentation = "Teacher with best or worst results obtained"
    teacher_name = SelectField(label="Teacher", coerce=int)
    criteria = SelectField(label="Criteria", coerce=int,
                           choices=[(0, "Best results obtained"),
                                    (1, "Worst results obtained")])
    submit = SubmitField("Show")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_name.choices = [(t.id, t.realname) for t in
                                     User.query.filter_by(role_id=Role.TEACHER).order_by('realname')]

    def validate(self):
        rv = super().validate()
        if not rv:
            return False
        return True


class TeacherDisciplinesStatisticForm(Form):
    presentation = "Disciplines given by a teacher"
    teacher_name = SelectField(label="Teacher", coerce=int)
    submit = SubmitField("Show")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher_name.choices = [(t.id, t.realname) for t in
                                     User.query.filter_by(role_id=Role.TEACHER).order_by('realname')]

    def validate(self):
        rv = super().validate()
        if not rv:
            return False
        return True
