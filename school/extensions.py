# -*- coding: utf-8 -*-
# init all the extensions instances
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from flask.ext.mail import Mail

mail = Mail()

from flask.ext.login import LoginManager

login_manager = LoginManager()

import sqlite3
from flask import g

DATABASE = 'db.sqlite'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()