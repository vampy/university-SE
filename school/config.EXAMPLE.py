# -*- config:utf-8 -*-
import os

FLASH_ERROR = "danger"
FLASH_WARNING = "warning"
FLASH_INFO = "info"
FLASH_SUCCESS = "success"


class Config:
    # Get app root path, also can use flask.root_path. when in an app context
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Flask Config
    # http://flask.pocoo.org/docs/0.10/config/#builtin-configuration-values
    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = '#################################################'
    DEBUG = True

    # Debug Toolbar
    # https://flask-debugtoolbar.readthedocs.org/en/latest/#configuration
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # SQL ALCHEMY Config
    # https://pythonhosted.org/Flask-SQLAlchemy/config.html
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + PROJECT_ROOT + '/db.sqlite'

    # WTF forms config
    # https://flask-wtf.readthedocs.org/en/latest/config.html
    # Enable protection against *Cross-site Request Forgery (CSRF)*
    WTF_CSRF_ENABLED = False

    # disable logging
    LOGIN_DISABLED = False

    #  Mail setting
    # https://pythonhosted.org/flask-mail/#configuring-flask-mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
