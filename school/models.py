"""
General project models used.
These may get moved to a blueprint/package at any time
"""
from school.extensions import db
from sqlalchemy import Column, Integer, String, ForeignKey, \
    Date, SmallInteger, Boolean, PrimaryKeyConstraint, and_
from datetime import date


# keep track of each student in what group, could just keep a column in users table
group_students = db.Table(
    "group_students",
    Column("group_id", Integer, ForeignKey("groups.id"), nullable=False),
    Column("student_id", Integer, ForeignKey("users.id"), nullable=False, unique=True),
    PrimaryKeyConstraint('group_id', 'student_id')  # a student can be in only one group at a time
)

# Each degree period has specific groups
class Group(db.Model):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    degree_period_id = Column(Integer, ForeignKey("degree_periods.id"))
    name = Column(String(64), nullable=False)  # 911, G922

    degree_period = db.relationship("DegreePeriod")
    students = db.relationship("User",
                               secondary=group_students,
                               lazy="dynamic",
                               backref=db.backref("groups", lazy="dynamic"))

    def __repr__(self):
        return '<Group id={0}, name={1}>'.format(self.id, self.name)

# every department can have multiple degrees, and every degree can be part of multiple departments?
# example: Math and Computer Science department can Have Computer Science in English, Math in Romanian
department_degrees = db.Table(
    "department_degrees",
    Column("department_id", Integer, ForeignKey("departments.id"), nullable=False),
    Column("degree_id", Integer, ForeignKey("degrees.id"), nullable=False),
    PrimaryKeyConstraint('department_id', 'degree_id')
)

# every department has chiefs, aka admins for that department
department_chiefs = db.Table(
    "department_chiefs",
    Column("chief_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("department_id", Integer, ForeignKey("departments.id"), nullable=False),
    PrimaryKeyConstraint('chief_id'),  # a user can be only part of one department
)


# every teacher is part of an department
department_teachers = db.Table(
    "department_teachers",
    Column("teacher_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("department_id", Integer, ForeignKey("departments.id"), nullable=False),
    PrimaryKeyConstraint('teacher_id'),  # a user can be only part of one department
)


class Department(db.Model):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    degrees = db.relationship("Degree",
                              secondary=department_degrees,
                              backref=db.backref("departments", lazy="dynamic"))
    chiefs = db.relationship("User",
                             secondary=department_chiefs,
                             backref=db.backref("department_cd", lazy="dynamic"))
    teachers = db.relationship("User",
                               secondary=department_teachers,
                               backref=db.backref("department_teacher", lazy="dynamic"))

    def __repr__(self):
        return '<Departament id={0}, name={1}>'.format(self.id, self.name)


class Language(db.Model):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    degrees = db.relationship("DegreePeriod", backref="language", lazy="dynamic")

    def __repr__(self):
        return '<Language id={0}, name={1}>'.format(self.id, self.name)


# each teacher can have one or two qualifications
class QualificationType:
    LECTURER = 1
    ASSISTANT = 2


# keep track of qualifications of each teacher
class Qualification(db.Model):
    __tablename__ = "qualifications"

    teacher_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    type_id = Column(SmallInteger, default=QualificationType.LECTURER)

    teacher = db.relationship("User", backref=db.backref("qualification", lazy="dynamic"))

    def is_lecturer(self):
        return self.type_id == QualificationType.LECTURER

    def is_assistant(self):
        return self.type_id == QualificationType.ASSISTANT

    def type_to_str(self):
        if self.type_id == QualificationType.LECTURER:
            return "lecturer"
        elif self.type_id == QualificationType.ASSISTANT:
            return "assistant"
        else:
            return "invalid type"

    def __repr__(self):
        return "<Qualification teacher_id={0}, type_id={1}>".format(self.teacher_id, self.type_to_str())


class DegreeType:
    UNDERGRADUATE = 1
    GRADUATE = 2


# See DegreePeriod for language
class Degree(db.Model):
    __tablename__ = "degrees"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    type_id = Column(SmallInteger, default=DegreeType.UNDERGRADUATE)
    courses = db.relationship("Course", backref="degree", lazy="dynamic")

    def __repr__(self):
        return '<Degree id={0}, name={1}, type_id={2}'.format(self.id, self.name, self.type_id)

    def is_undergraduate(self):
        return self.type_id == DegreeType.UNDERGRADUATE

    def is_graduate(self):
        return self.type_id == DegreeType.GRADUATE

# Connection between degree and student
degrees_period_students = db.Table(
    "degree_period_students",
    Column("student_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("degree_period_id", Integer, ForeignKey("degree_periods.id"), nullable=False),
    PrimaryKeyConstraint('student_id', 'degree_period_id')
)

# Each degree can have different periods, Computer science 3 years English, Computer Science 4 years German, etc
class DegreePeriod(db.Model):
    __tablename__ = "degree_periods"

    id = Column(Integer, primary_key=True)
    degree_id = Column(Integer, ForeignKey("degrees.id"))
    language_id = Column(Integer, ForeignKey("languages.id"), default=None, nullable=True)
    semester_start_id = Column(Integer, ForeignKey("semesters.id"))
    semester_end_id = Column(Integer, ForeignKey("semesters.id"))

    degree = db.relationship("Degree")
    semester_start = db.relationship("Semester", foreign_keys=[semester_start_id])
    semester_end = db.relationship("Semester", foreign_keys=[semester_end_id])
    # has back reference 'language' from Language Model
    # has back reference 'students' from User Model

    def __repr__(self):
        return '<DegreePeriod id={0}, degree_id={1}, language_id={2}, semester_start_id={3}, semester_end_id={4}>'.format(
            self.id, self.degree_id, self.language_id, self.semester_start_id, self.semester_end_id)


# each course has it's own degree
# If a optional course it is proposed, the entry it is first added to this table
# along side the Teaches table, to keep track in what semester the optional course is taught
class Course(db.Model):
    __tablename__ = "courses"
    # TODO add min_students, max_students
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    category = Column(SmallInteger, default=1)  # category 1 is obligatory courses
    degree_id = Column(Integer, ForeignKey("degrees.id"))
    # has back reference 'degree' from Degree model
    # has back reference 'semesters' from Semester model

    # optional course
    is_optional = Column(Boolean, default=False)  # is course optional

    # the teacher who proposed the course is in the Teachers table and has one entry there
    is_approved = Column(Boolean, default=True)
    approval_reason = Column(String(256), nullable=True, default=None)

    @classmethod
    def get_by_id(cls, course_id):
        return cls.query.filter_by(id=course_id).first_or_404()

    def __repr__(self):
        return '<Course id={0}, name={1}, is_optional={2}, degree_id={3}, is_approved={4}, reason={5}>'.format(
            self.id, self.name, self.is_optional, self.degree_id, self.is_approved, self.approval_reason)

# each course is part of a semester, from this list a student will choose the obligatory courses
# and the optional ones
semester_courses = db.Table(
    "semester_courses",
    Column("course_id", Integer, ForeignKey("courses.id"), nullable=False),
    Column("semester_id", Integer, ForeignKey("semesters.id"), nullable=False),
)

# Mark a semester as signed in the contract, students are not allowed to modify enrollment
# Each contract is a unique per student/semester/degree, I added degree because the student
# may be at 2 degrees in the same semester
class ContractSemester(db.Model):
    __tablename__ = "semester_contracts"

    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    degree_id = Column(Integer, ForeignKey("degrees.id"), primary_key=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), primary_key=True)
    date_sign = Column(Date, default=date.today())

    student = db.relationship("User")
    semester = db.relationship("Semester")
    degree = db.relationship("Degree")

    def __repr__(self):
        return "<ContractSemester student_id={0}, degree_id={1}, semester_id={2}, date_sign={3}>".format(
            self.student_id, self.degree_id, self.semester_id, self.date_sign)


# to select all courses of a degree: semester.courses where degree == degree.id
class Semester(db.Model):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)  # human readable semester name
    year = Column(Integer)  # the semester year, 2014, 2015
    date_start = Column(Date)  # september 2014
    date_end = Column(Date)  # june 2015
    courses = db.relationship("Course", secondary=semester_courses, backref=db.backref("semesters", lazy="dynamic"))

    @staticmethod
    def get_semesters_year(year):
        return Semester.query.filter_by(year=year).order_by(Semester.date_start.asc()).all()

    @staticmethod
    def get_semesters(date_start, date_end):
        return Semester.query.filter(and_(Semester.date_start >= date_start, Semester.date_end <= date_end)) \
            .order_by(Semester.year.asc(), Semester.date_start.asc()).all()

    @classmethod
    def get_by_id(cls, semester_id):
        return cls.query.filter_by(id=semester_id).first_or_404()

    def __repr__(self):
        return '<Semester id={0}, name={1}, year={2}, date_start={3}, date_end={4}>'.format(
            self.id, self.name, self.year, self.date_start, self.date_end)


# keeps track of each teacher teaches what course in what semester
class Teaches(db.Model):
    __tablename__ = "teaches"

    teacher_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), primary_key=True)
    teacher = db.relationship("User")
    course = db.relationship("Course")
    semester = db.relationship("Semester")

    @staticmethod
    def get_optional_courses(teacher, year):
        """
        Find all optional course for a teacher in a year
        :param teacher: the teacher we want to find the optional course for
        :param year: the year we want to find the optional courses
        :return: a list of Teaches
        """
        return Teaches.query.join(Course).join(Semester). \
            filter(and_(Teaches.teacher_id == teacher.id, Course.is_optional == True, Semester.year == year)).all()

    def __repr__(self):
        return '<Teaches tid={0}, cid={1}, sem_id={2}>'.format(self.teacher_id, self.course_id, self.semester_id)


# keeps track each student at what course he is enrolled in, and in what semester
# If there is an entry in the contract with this semester and student, users should not be allowed to modify enrollment
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
