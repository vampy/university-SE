from flask.ext.login import login_required
from flask import Blueprint, render_template, flash, redirect, url_for
from school.decorators import role_required
from school.config import FLASH_ERROR
from .forms import SelectStatisticForm, TeacherWBOWROStatisticForm, OrderedStudentsStatisticFrom, TeacherDisciplinesStatisticForm
from school.models import *
from sqlalchemy import func
from sqlalchemy import desc
from school.user import User

statistics = Blueprint("statistics", __name__)


@statistics.route('/statistics', methods=['GET', 'POST'])
@login_required
# Statistics are available only for admins and chief departments.
@role_required(admin=True, cd=True)
def see_statistics():
    select_statistic_form = SelectStatisticForm()
    if select_statistic_form.validate_on_submit():
        if select_statistic_form.selected_statistic.data == 0:
            return redirect(url_for('statistics.generate', statistic_id=select_statistic_form.selected_statistic.data))
        if select_statistic_form.selected_statistic.data == 1:

            return redirect(url_for('statistics.generate', statistic_id=select_statistic_form.selected_statistic.data))
        if select_statistic_form.selected_statistic.data == 2:
            return redirect(url_for('statistics.generate', statistic_id=select_statistic_form.selected_statistic.data))
    return render_template("statistics/see_statistics.html", form=select_statistic_form)


@statistics.route('/statistics/<int:statistic_id>', methods=["GET", "POST"])
def generate(statistic_id):
    if statistic_id == 0:
        ordered_students_statistic_form = OrderedStudentsStatisticFrom()
        if ordered_students_statistic_form.validate_on_submit():

            subquery=db.session.query(User.id, User.realname.label("users_realname"), Group.name.label("groups_name"),
                          func.avg(Enrollment.grade).label("average_mark"), Semester.year.label("semester_start_year")).join(Group.students)\
                          .join(Enrollment).group_by(Enrollment.student_id).filter(Enrollment.grade > 0).join(degrees_period_students).join(DegreePeriod).\
                          join(Semester, Semester.id == DegreePeriod.semester_start_id)


            from_each = ordered_students_statistic_form.from_each.data
            # from each group
            if from_each == 0:
                subquery_2 = subquery.order_by("groups_name")
            # from each year
            elif from_each == 1:
                subquery_2 = subquery.order_by("semester_start_year")

            order_by = ordered_students_statistic_form.order.data
            # order by average mark (decreasing)
            if order_by == 0:
                subquery_3_result = subquery_2.order_by(desc("average_mark")).all()
            # order by name (alphabetically)
            elif order_by ==1:
                subquery_3_result = subquery_2.order_by("users_realname").all()



            lower_bound = ordered_students_statistic_form.average_mark_lower_bound.data
            upper_bound = ordered_students_statistic_form.average_mark_upper_bound.data

            result_table = []
            for result in subquery_3_result:
                if lower_bound < result.average_mark < upper_bound:
                    result_table.append(result)
            if len(result_table) == 0:
                flash("There is no data for this statistic", FLASH_ERROR)
            else:
                return render_template("statistics/ordered_students_statistic.html", from_each=from_each, order_by=order_by,
                                        lower_bound=lower_bound, upper_bound=upper_bound, result_table=result_table)
        return render_template("statistics/generate_statistic.html", statistic_id=statistic_id, form=ordered_students_statistic_form)

    elif statistic_id == 1:
        teacher_wbowro_statistic_form = TeacherWBOWROStatisticForm()
        if teacher_wbowro_statistic_form.validate_on_submit():
            subquery = db.session.query(User.realname.label("users_realname"), Course.name.label("courses_name"), func.count(User.id).label("no_of_students"), func.avg(Enrollment.grade).label("average_mark")).join(Teaches).join(Course).join(Enrollment).filter(Enrollment.grade > 0).join(User, User.id == Enrollment.student_id, aliased=True).group_by(Course.id)
            best_0_or_worst_1 = teacher_wbowro_statistic_form.criteria.data
            # it is wanted the teacher with the best results obtained
            if best_0_or_worst_1 == 0:
                result_table = subquery.order_by(desc("average_mark")).all()
            # it is wanted the teacher with the worst results obtained
            elif best_0_or_worst_1 == 1:
                result_table = subquery.order_by("average_mark").all()
            index = 0
            teacher_table = [result_table[index]]
            # in case there is more than one teacher with best/worst results obtained
            while result_table[index].average_mark == result_table[index+1].average_mark:
                index += 1
                teacher_table.append(result_table[index])
            if len(teacher_table) == 0:
                flash("There is no data for this statistic", FLASH_ERROR)
            else:
                return render_template("statistics/best_or_worst_teacher_results_statistic.html", best_0_or_worst_1=best_0_or_worst_1,
                                       teacher_table=teacher_table)
        return render_template("statistics/generate_statistic.html", statistic_id=statistic_id,
                               form=teacher_wbowro_statistic_form)

    elif statistic_id == 2:
        teacher_disciplines_statistic_form = TeacherDisciplinesStatisticForm()

        if teacher_disciplines_statistic_form.validate_on_submit():
            teacher_id = teacher_disciplines_statistic_form.teacher_name.data
            for choice in teacher_disciplines_statistic_form.teacher_name.choices:
                if choice[0] == teacher_id:
                    teacher_name = choice[1]
            statistics_table = db.session.query(Course.name.label("courses_name"), Course.category.label("courses_category"), Course.is_optional.label("courses_is_optional"), Degree.name.label("degrees_name"), Degree.type_id.label("degrees_type_id"), Language.name.label("languages_name"), func.count(User.id).label("no_of_students"))\
                .group_by(Course.id).join(Teaches).join(Degree).join(DegreePeriod).join(Language)\
                .join(Enrollment, Enrollment.course_id == Course.id).join(User, User.id == Enrollment.student_id).filter(Teaches.teacher_id == teacher_id).all()

            if len(statistics_table) == 0:
                flash("There is no data for this statistic", FLASH_ERROR)
            else:
                return render_template("statistics/teacher_disciplines_statistic.html", teacher_name=teacher_name,
                                       statistics_table=statistics_table)

        return render_template("statistics/generate_statistic.html", statistic_id=statistic_id, form=teacher_disciplines_statistic_form)
    else:
        return redirect(url_for('statistics.see_statistics'))
