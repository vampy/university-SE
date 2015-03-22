#!/usr/bin/python3
from school import create_app
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
def initdb():
    """
    Init/reset database
    """
    db.drop_all()
    db.create_all()

    print('DB initialized')

if __name__ == "__main__":
    manager.run()