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
        return '<Group id={0}, name={1}>'.format(self.id, self.name)


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
        return '<Departament id={0}, name={1}>'.format(self.id, self.name)


class Language(db.Model):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    degrees = db.relationship("Degree", backref="language", lazy="dynamic")

    def __repr__(self):
        return '<Language id={0}, name={1}>'.format(self.id, self.name)


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
        return '<Degree id={0}, name={1}, type_id={2}, language_id={3}>'.format(self.id, self.name,
                                                                                self.type_id,
                                                                                self.type_id)

    def is_undergraduate(self):
        return self.type_id == DegreeType.UNDERGRADUATE

    def is_graduate(self):
        return self.type_id == DegreeType.GRADUATE


# Each degree can have different periods, Computer science 3 years, Computer Science 4 years, etc
class DegreePeriod(db.Model):
    __tablename__ = "degree_period"

    id = Column(Integer, primary_key=True)
    degree_id = Column(Integer, ForeignKey("degrees.id"))
    semester_start_id = Column(Integer, ForeignKey("semesters.id"))
    semester_end_id = Column(Integer, ForeignKey("semesters.id"))

    degree = db.relationship("Degree")
    semester_start = db.relationship("Semester", foreign_keys=[semester_start_id])
    semester_end = db.relationship("Semester", foreign_keys=[semester_end_id])

    def __repr__(self):
        return '<DegreePeriod id={0}, degree_id={1}, semester_start_id={2}, semester_end_id={3}'.format(
            self.id, self.degree_id, self.semester_start_id, self.semester_end_id)


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
        return '<Course id={0}, name={1}, is_optional={2}, degree_id={3}>'.format(self.id, self.name,
                                                                                  self.is_optional,
                                                                                  self.degree_id)

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
        return '<Semester id={0}, name={1}, year={2}, date_start={3}, date_end={4}>'.format(self.id,
                                                                                            self.name,
                                                                                            self.year,
                                                                                            self.date_start,
                                                                                            self.date_end)


# keeps track of each teacher teaches what course in what semester
class Teaches(db.Model):
    __tablename__ = "teaches"

    teacher_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), primary_key=True)
    teacher = db.relationship("User")
    course = db.relationship("Course")
    semester = db.relationship("Semester")

    def __repr__(self):
        return '<Teaches tid={0}, cid={1}, sem_id={2}>'.format(self.teacher_id, self.course_id, self.semester_id)


# keeps track each student at what course he is enrolled in, and in what semester
class Enrollment(db.Model):
    __tablename__ = "enrollment"

    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), primary_key=True)
    grade = Column(Integer, default=0)
    date_grade = Column(Date, default=None, nullable=True)  # The date he got the grade

    # maybe use lazy dynamic
    student = db.relationship("User")
    course = db.relationship("Course")
    semester = db.relationship("Semester")

    def __repr__(self):
        return '<Enrollment sid={0}, cid={1}, sem_id={2}, grade={3}>'.format(self.student_id, self.course_id,
                                                                             self.semester_id, self.grade)
