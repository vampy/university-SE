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

    #############################################################################
    # School settings for the current app
    #############################################################################
    # User Model
    APP_USER_USERNAME_MIN = 2
    APP_USER_USERNAME_MAX = 64
    APP_USER_REALNAME_MAX = 128
    APP_USER_EMAIL_MAX = 64
    APP_USER_PASSWORD_MIN = 7

    # Group Model
    APP_GROUP_NAME_MIN = 3
    APP_GROUP_NAME_MAX = 64

    # Department Model
    APP_DEPARTMENT_NAME_MIN = 4
    APP_DEPARTMENT_NAME_MAX = 64

    # Language Model
    APP_LANGUAGE_NAME_MIN = 4
    APP_LANGUAGE_NAME_MAX = 64

    # Degree Model
    APP_DEGREE_NAME_MIN = 4
    APP_DEGREE_NAME_MAX = 64

    # Course Model
    APP_COURSE_NAME_MIN = 4
    APP_COURSE_NAME_MAX = 64
    APP_COURSE_MIN_STUDENTS = 20
    APP_COURSE_MAX_STUDENTS = 4096
    APP_COURSE_MAX_STUDENTS_OPTIONAL = 80  # max students for optional course
    APP_COURSE_CREDITS = 6
    APP_COURSE_CATEGORY = 1
    APP_COURSE_CATEGORY_OPTIONAL = 2  # default category for optional course

    # Semester Model
    APP_SEMESTER_NAME_MIN = 4
    APP_SEMESTER_NAME_MAX = 64

