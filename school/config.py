# -*- config:utf-8 -*-


class Config():
    DEBUG = True

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = False

    # disable logging
    LOGIN_DISABLED = True

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = 'secret key'