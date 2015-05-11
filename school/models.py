"""
General project models used.
These may get moved to a blueprint/package at any time
"""
from school.extensions import db
from sqlalchemy import Column, Integer, String, ForeignKey, \
    Date, SmallInteger, Boolean, PrimaryKeyConstraint


# keep track of each student in what group, could just keep a column in users table
# but it would complicate things with roles, as teachers, admins do not have groups associated with it
group_students = db.Table(
    "group_students",
    Column("group_id", Integer, ForeignKey("groups.id"), nullable=False),
    Column("student_id", Integer, ForeignKey("users.id"), nullable=False, unique=True),
    PrimaryKeyConstraint('group_id', 'student_id')  # a student can be in only one group at a time
)


class Group(db.Model):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)  # 911, G922
    students = db.relationship("User",
                               secondary=group_students,
                               backref=db.backref("group", lazy="dynamic"))

    def __repr__(self):
        return '<Group id={0}, name={1}>'.format(str(self.id), str(self.name))


# TODO maybe every degree has a department type
# every department can have multiple degrees
# example: Math and Computer Science department can Have Computer Science in English, Math in Romanian
department_degrees = db.Table(
    "departments_degrees",
    Column("department_id", Integer, ForeignKey("departments.id"), nullable=False),
    Column("degree_id", Integer, ForeignKey("degrees.id"), nullable=False),
    PrimaryKeyConstraint('department_id', 'degree_id')
)


class Department(db.Model):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    degrees = db.relationship("Degree",
                              secondary=department_degrees,
                              backref=db.backref("departments", lazy="dynamic"))

    def __repr__(self):
        return '<Departament id={0}, name={1}>'.format(str(self.id), str(self.name))


class Language(db.Model):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    degrees = db.relationship("Degree", backref="language", lazy="dynamic")

    def __repr__(self):
        return '<Language id={0}, name={1}>'.format(str(self.id), str(self.name))


class DegreeType:
    UNDERGRADUATE = 1
    GRADUATE = 2


# TODO add degree period, degree <-> student, period_start, period_end, semesters number
# each degree has a language, eg: CS English, CS Romanian, etc
class Degree(db.Model):
    __tablename__ = "degrees"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    type_id = Column(SmallInteger, default=DegreeType.UNDERGRADUATE)
    language_id = Column(Integer, ForeignKey("languages.id"), default=None, nullable=True)
    courses = db.relationship("Course", backref="degree", lazy="dynamic")

    def __repr__(self):
        return '<Degree id={0}, name={1}, type_id={2}, language_id={3}>'.format(str(self.id), str(self.name),
                                                                                str(self.type_id),
                                                                                str(self.type_id))

    def is_undergraduate(self):
        return self.type_id == DegreeType.UNDERGRADUATE

    def is_graduate(self):
        return self.type_id == DegreeType.GRADUATE


# each course has it's own degree
# If a optional course it is proposed, the entry it is first added to this table
# along side the Teaches table, to keep track in what semester the optional course is taught
class Course(db.Model):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    is_optional = Column(Boolean, default=False)  # is course optional

    # the teacher who proposed the course
    proposed_by = Column(Integer, ForeignKey("users.id"), nullable=True, default=None)

    # the CD who approved the course
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True, default=None)
    degree_id = Column(Integer, ForeignKey("degrees.id"))

    proposed_user = db.relationship("User", foreign_keys=[proposed_by])
    approved_user = db.relationship("User", foreign_keys=[approved_by])

    def __repr__(self):
        return '<Course id={0}, name={1}, is_optional={2}, degree_id={3}>'.format(str(self.id), str(self.name),
                                                                                  str(self.is_optional),
                                                                                  str(self.degree_id))

# each course is part of a semester
semester_courses = db.Table(
    "semester_courses",
    Column("course_id", Integer, ForeignKey("courses.id"), nullable=False),
    Column("semester_id", Integer, ForeignKey("semesters.id"), nullable=False),
)


# to select all courses of a degree: semester.courses where degree == degree.id
class Semester(db.Model):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)  # human readable semester name
    year = Column(Integer)  # the semester year, 2014, 2015
    date_start = Column(Date)  # september 2014
    date_end = Column(Date)  # june 2015
    courses = db.relationship("Course", secondary=semester_courses, backref=db.backref("semesters", lazy="dynamic"))

    def __repr__(self):
        return '<Semester id={0}, name={1}, year={2}, date_start={3}, date_end={4}>'.format(str(self.id),
                                                                                            str(self.name),
                                                                                            str(self.year),
                                                                                            str(self.date_start),
                                                                                            str(self.date_end))


class Teaches(db.Model):
    __tablename__ = "teaches"

    teacher_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), primary_key=True)
    teacher = db.relationship("User")
    course = db.relationship("Course")
    semester = db.relationship("Semester")

    def __repr__(self):
        return '<Teaches tid={0}, cid={1}, sem_id={2}>'.format(str(self.teacher_id), str(self.course_id),
                                                               str(self.semester_id))


class Enrollment(db.Model):
    __tablename__ = "enrollment"

    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), primary_key=True)
    grade = Column(Integer, default=0)
    # maybe use lazy dynamic
    student = db.relationship("User")
    course = db.relationship("Course")
    semester = db.relationship("Semester")

    def __repr__(self):
        return '<Enrollment sid={0}, cid={1}, sem_id={2}, grade={3}>'.format(str(self.student_id), str(self.course_id),
                                                                             str(self.semester_id, str(self.grade)))
