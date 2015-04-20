#!/usr/bin/python3
from school import create_app
from school.user import User
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

    db.session.add(test_user)
    db.session.commit()

    print('DB initialized')

if __name__ == "__main__":
    manager.run()
