# -*- coding: utf-8 -*-
# init all the extensions instances
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from flask.ext.mail import Mail

mail = Mail()

from flask.ext.login import LoginManager

login_manager = LoginManager()

from flask_debugtoolbar import DebugToolbarExtension

toolbar = DebugToolbarExtension()
