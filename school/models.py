"""
General project models used.
These may get moved to a blueprint/package at any time
"""
from school.extensions import db
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, PrimaryKeyConstraint


class Course(db.Model):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    is_optional = Column(Boolean, default=False)  # is course optional


class Semester(db.Model):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    year = Column(Integer)

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


