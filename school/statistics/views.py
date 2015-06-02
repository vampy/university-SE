from flask.ext.login import login_required
from flask import Blueprint, render_template, flash, redirect, url_for
from school.decorators import role_required
from school.config import FLASH_ERROR
from .forms import SelectStatisticForm, TeacherWBOWROStatisticForm, \
    OrderedStudentsStatisticFrom, \
    TeacherDisciplinesStatisticForm, Statistic
from school.models import *
from sqlalchemy import func, desc, distinct
from school.user import User

statistics = Blueprint("statistics", __name__)

# Statistics are available only for admins and chief departments.
@statistics.route('/statistics', methods=['GET', 'POST'])
@login_required
@role_required(admin=True, cd=True)
def see_statistics():
    form = SelectStatisticForm()
    if form.validate_on_submit():
        selected = form.selected_statistic.data
        if selected == Statistic.ORDERED_STUDENTS:
            return redirect(url_for('statistics.generate', statistic_id=selected))
        if selected == Statistic.TEACHER_RANKING:
            return redirect(url_for('statistics.generate', statistic_id=selected))
        if selected == Statistic.TEACHER_DISCIPLINES:
            return redirect(url_for('statistics.generate', statistic_id=selected))
    return render_template("statistics/see_statistics.html", form=form)


@statistics.route('/statistics/<int:statistic_id>', methods=["GET", "POST"])
def generate(statistic_id):
    if statistic_id == Statistic.ORDERED_STUDENTS:
        form = OrderedStudentsStatisticFrom()
        if form.validate_on_submit():

            subquery = db.session.query(User.id,
                                        User.realname.label("users_realname"),
                                        Group.name.label("groups_name"),
                                        func.avg(Enrollment.grade).label("average_mark"),
                                        Semester.year.label("semester_start_year")) \
                .join(Group.students) \
                .join(Enrollment).group_by(Enrollment.student_id).filter(Enrollment.grade > 0) \
                .join(degrees_period_students).join(DegreePeriod) \
                .join(Semester, Semester.id == DegreePeriod.semester_start_id)

            subquery_2 = None
            from_each = form.from_each.data
            # from each group
            if from_each == 0:
                subquery_2 = subquery.order_by("groups_name")

            # from each year
            elif from_each == 1:
                subquery_2 = subquery.order_by("semester_start_year")
            assert subquery_2 is not None

            subquery_3_result = None
            order_by = form.order.data
            # order by average mark (decreasing)
            if order_by == 0:
                subquery_3_result = subquery_2.order_by(desc("average_mark")).all()

            # order by name (alphabetically)
            elif order_by == 1:
                subquery_3_result = subquery_2.order_by("users_realname").all()
            assert subquery_3_result is not None

            lower_bound = form.average_mark_lower_bound.data
            upper_bound = form.average_mark_upper_bound.data

            # only take marks in specified range
            result_table = []
            for result in subquery_3_result:
                if lower_bound < result.average_mark < upper_bound:
                    result_table.append(result)

            if not result_table:
                flash("There is no data for this statistic", FLASH_ERROR)
            else:
                return render_template("statistics/ordered_students_statistic.html", from_each=from_each,
                                       order_by=order_by,
                                       lower_bound=lower_bound, upper_bound=upper_bound, result_table=result_table)
        return render_template("statistics/generate_statistic.html", statistic_id=statistic_id, form=form)

    elif statistic_id == Statistic.TEACHER_RANKING:
        form = TeacherWBOWROStatisticForm()
        if form.validate_on_submit():
            subquery = db.session.query(User.realname.label("users_realname"),
                                        Course.name.label("courses_name"),
                                        func.count(distinct(Enrollment.student_id)).label("no_of_students"),
                                        func.avg(Enrollment.grade).label("average_mark")) \
                .join(Teaches).join(Course).join(Enrollment).filter(Enrollment.grade > 0) \
                .join(User, User.id == Enrollment.student_id, aliased=True).group_by(Course.id)

            result_table = None
            best_0_or_worst_1 = form.criteria.data
            # it is wanted the teacher with the best results obtained
            if best_0_or_worst_1 == 0:
                result_table = subquery.order_by(desc("average_mark")).all()

            # it is wanted the teacher with the worst results obtained
            elif best_0_or_worst_1 == 1:
                result_table = subquery.order_by("average_mark").all()
            assert result_table is not None

            index = 0
            teacher_table = [result_table[index]]
            # in case there is more than one teacher with best/worst results obtained
            while result_table[index].average_mark == result_table[index + 1].average_mark:
                index += 1
                teacher_table.append(result_table[index])

            if not teacher_table:
                flash("There is no data for this statistic", FLASH_ERROR)
            else:
                return render_template("statistics/best_or_worst_teacher_results_statistic.html",
                                       best_0_or_worst_1=best_0_or_worst_1,
                                       teacher_table=teacher_table)
        return render_template("statistics/generate_statistic.html", statistic_id=statistic_id, form=form)

    elif statistic_id == Statistic.TEACHER_DISCIPLINES:
        form = TeacherDisciplinesStatisticForm()

        if form.validate_on_submit():
            selected_teacher_id = form.teacher_name.data

            # find teacher name
            teacher_name = None
            for choice in form.teacher_name.choices:
                if choice[0] == selected_teacher_id:
                    teacher_name = choice[1]
                    break
            assert teacher_name is not None

            statistics_table = db.session.query(Course.name.label("courses_name"),
                                                Course.type_id.label("courses_type"),
                                                Course.is_optional.label("courses_is_optional"),
                                                Degree.name.label("degrees_name"),
                                                Degree.type_id.label("degrees_type_id"),
                                                Language.name.label("languages_name"),
                                                func.count(distinct(Enrollment.student_id)).label("no_of_students")) \
                .group_by(Course.id).join(Teaches).join(Degree).join(DegreePeriod).join(Language) \
                .join(Enrollment, Enrollment.course_id == Course.id) \
                .join(User, User.id == Enrollment.student_id) \
                .filter(Teaches.teacher_id == selected_teacher_id).all()

            if not statistics_table:
                flash("There is no data for this statistic", FLASH_ERROR)
            else:
                return render_template("statistics/teacher_disciplines_statistic.html", teacher_name=teacher_name,
                                       statistics_table=statistics_table)

        return render_template("statistics/generate_statistic.html", statistic_id=statistic_id, form=form)

    # default page
    return redirect(url_for('statistics.see_statistics'))
