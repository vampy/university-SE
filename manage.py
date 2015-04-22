#!/usr/bin/python3
from school import create_app
from school.user import User
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

    test_user = User(
        username="test",
        password="test",
        realname="John Doe",
        email="example@example.com"
    )
    test_group = Group(name="911")
    db.session.add(test_group)

    test_group.students.append(test_user)

    test_course = Course(name="SE", is_optional=True)
    db.session.add(test_course)
    db.session.add(test_user)
    db.session.commit()

    print('DB initialized')

if __name__ == "__main__":
    manager.run()
