from school.extensions import db
from sqlalchemy import Column, Integer, String, SmallInteger
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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
    password_hash = Column(String(160), nullable=False)
    role_id = Column(SmallInteger, default=Role.STUDENT)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        # invalid role detected
        if self.role_id not in Role.get_roles():
            self.role_id = Role.STUDENT
            print("ERROR: INVALID role_id")

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

    def get_realname(self):
        return self.realname

    def get_username(self):
        return self.username

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
