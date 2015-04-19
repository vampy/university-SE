# -*- config:utf-8 -*-


class Config:
    DEBUG = True

    # listen to 0.0.0.0 for other users in the network to see your server
    HOST = "0.0.0.0"

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = False

    # disable logging
    LOGIN_DISABLED = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = 'secret key'