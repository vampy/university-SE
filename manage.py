#!/usr/bin/python3
from school import create_app
from school.user import User
from school.user.models import Role
from school.models import Course, Semester, Group
from flask.ext.script import Manager
from school.extensions import db

app = create_app()
manager = Manager(app)

@manager.command
def run():
    """
    Run local app
    """
    app.run()

@manager.command
def init():
    """
    Init/reset database
    """
    db.drop_all()
    db.create_all()

    # Add users
    # student
    test_user = User(
        username="test",
        password="test",
        realname="John Doe",
        email="example@example.com"
    )
    # teacher
    test_teacher = User(
        username="teacher",
        password="teacher",
        realname="Dan Chiorean",
        email="dan@chiorean.com",
        role_id=Role.TEACHER
    )
    # chief_department

    test_chief_department = User(
        username="cd",
        password="cd",
        realname="Dan Chiorean",
        email="danchiorean@cd.com",
        role_id=Role.CHIEF_DEPARTMENT
    )
    # admin
    test_admin = User(
        username="admin",
        password="admin",
        realname="Thor",
        email="admin@example.com",
        role_id=Role.ADMIN
    )
    test_group = Group(name="911")
    db.session.add(test_group)

    test_group.students.append(test_user)
    db.session.add(test_user)
    db.session.add(test_teacher)
    db.session.add(test_chief_department)
    db.session.add(test_admin)
    db.session.commit()

    print('DB initialized')

if __name__ == "__main__":
    manager.run()
