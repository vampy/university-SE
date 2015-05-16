from flask import Flask, render_template, url_for

from .frontend import frontend
from .config import Config
from .extensions import *
from .user import User, user
from .course import course
from .admin import admin

import os


def create_app():
    app = Flask(__name__)

    # configure app
    app.config.from_object(Config)

    # configure extensions
    db.init_app(app)
    app.config.update(dict(
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        MAIL_USE_SSL = False,
        MAIL_USERNAME = 'academicinfo.seproject@gmail.com',
        MAIL_PASSWORD = 'cldBwFYL',
    ))
    mail.init_app(app)
    login_manager.init_app(app)
    toolbar.init_app(app)

    # default login page, see https://flask-login.readthedocs.org/en/latest/#customizing-the-login-process
    login_manager.login_view = "frontend.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # configure blueprints
    blueprints = [frontend, user, course, admin]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    # handle common error pages
    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500

    # static url cache buster, see http://flask.pocoo.org/snippets/40/
    @app.context_processor
    def override_url_for():
        return {"url_for": dated_url_for}

    def dated_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                file_path = os.path.join(app.root_path, endpoint, filename)
                values['q'] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)

    return app
