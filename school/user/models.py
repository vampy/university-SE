from school.extensions import db
from sqlalchemy import Column, Integer, String, SmallInteger
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as TJSONWebSigSerializer, BadSignature, SignatureExpired
from flask import current_app

from school.config import FLASH_ERROR
from flask import flash

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
    # TODO try to use backref
    enrolled = db.relationship("Enrollment", lazy="dynamic", cascade="save-update, merge, delete, delete-orphan")
    # has back reference 'group' from Groups Model

    # teacher or cd
    teaches = db.relationship("Teaches", lazy="dynamic", cascade="save-update, merge, delete, delete-orphan")
    # has back reference 'department' from Department Model for CD

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        # invalid role detected
        if self.role_id is not None and self.role_id not in Role.get_roles():
            print("ERROR: INVALID role_id: ", self.role_id)
            self.role_id = Role.STUDENT

    def get_token(self, expiration=86400):
        # expiration default = 24h
        s = TJSONWebSigSerializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'user': self.id}).decode('utf-8')


    @staticmethod
    def verify_token(token):
        s = TJSONWebSigSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user_id = data.get('user')
        if user_id:
            return User.query.get(user_id)
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
