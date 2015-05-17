from school.models import *
from sqlalchemy import Column, Integer, String, SmallInteger, and_
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as TJSONWebSigSerializer, BadSignature, SignatureExpired
from flask import current_app


class Role:
    STUDENT = 1
    TEACHER = 2
    CHIEF_DEPARTMENT = 3
    ADMIN = 4

    @staticmethod
    def get_roles():
        return [Role.STUDENT, Role.TEACHER, Role.CHIEF_DEPARTMENT, Role.ADMIN]


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True)
    realname = Column(String(128), nullable=True)
    email = Column(String(64), unique=True)
    active_token = Column(String(125), nullable=True, default=None)
    password_hash = Column(String(160), nullable=False)
    role_id = Column(SmallInteger, default=Role.STUDENT)

    # student
    enrolled = db.relationship("Enrollment", lazy="dynamic", cascade="save-update, merge, delete, delete-orphan")
    degree_periods = db.relationship("DegreePeriod",
                                     lazy="dynamic",
                                     secondary=degrees_period_students,
                                     backref=db.backref("students", lazy="dynamic"))
    # has back reference 'group' from Groups Model

    # teacher or cd
    teaches = db.relationship("Teaches", lazy="dynamic", cascade="save-update, merge, delete, delete-orphan")
    # has back reference 'department' from Department Model for CD

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # invalid role detected
        if self.role_id is not None and self.role_id not in Role.get_roles():
            print("ERROR: INVALID role_id: ", self.role_id)
            self.role_id = Role.STUDENT

    def get_department_cd(self):
        """
        Get the department administered by the current CD.
        Assumes that the current user is a chief of department
        :return: Department
        """
        assert self.is_chief_department()
        return self.department.first()

    def get_default_period(self):
        """
        Get the default degree period, this should be smarter and check what degree period is in the current year
        :return: DegreePeriod
        """
        return self.degree_periods.first()

    def get_courses_enrolled_semester(self, semester):
        """
        Get all the course the current has enrolled in a semester
        :param semester: of type Semester
        :return: a list of tuples, the tuple if of the form (Enrollment, Course)
        """
        # join with join(Course.semesters) to verify that the courses exist also in the semester, besides enrolled
        return db.session.query(Enrollment, Course).join(Course)\
            .filter(and_(Enrollment.semester_id == semester.id, Enrollment.student_id == self.id))\
            .all()

    def has_contract_signed(self, semester, degree):
        """
        Check if student has a contract signed corresponding to a degree and semester
        :param semester: of type Semester
        :param degree: of type Degree
        :return:
        """
        return ContractSemester.query.filter(
            and_(ContractSemester.student_id == self.id,
                 ContractSemester.degree_id == degree.id,
                 ContractSemester.semester_id == semester.id)).first() is not None

    @staticmethod
    def get_semesters_for_period(degree_period):
        if not degree_period:
            return []

        return Semester.get_semesters(degree_period.semester_start.date_start, degree_period.semester_end.date_end)

    def get_token(self, expiration=86400):
        """
        Generate token for user that expires by default in 24
        :param expiration: time in seconds
        :return: a string representing the token
        """
        s = TJSONWebSigSerializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        """
        Check if a token is valid
        :param token:
        :return: None if token is invalid, otherwise return the user the token is valid for
        """
        if not token:
            return None

        # verify token integrity
        s = TJSONWebSigSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token

        # verify token against user
        user_id = data.get('user')
        if user_id:
            user = User.query.get(user_id)
            if user.active_token != token:  # token does not match database
                return None
            return user

        return None

    def __repr__(self):
        return '<User id={0}, username={1}, realname={2}, email={3}, role={4}>'.format(self.id,
                                                                                       self.username,
                                                                                       self.realname,
                                                                                       self.email,
                                                                                       self.role_to_str())

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    def role_to_str(self):
        if self.role_id == Role.STUDENT:
            return "student"
        elif self.role_id == Role.TEACHER:
            return "teacher"
        elif self.role_id == Role.CHIEF_DEPARTMENT:
            return "chief_department"
        elif self.role_id == Role.ADMIN:
            return "admin"

    def is_student(self):
        return self.role_id == Role.STUDENT

    def is_teacher(self):
        return self.role_id == Role.TEACHER

    def is_chief_department(self):
        return self.role_id == Role.CHIEF_DEPARTMENT

    def is_admin(self):
        return self.role_id == Role.ADMIN

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
