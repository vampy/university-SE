from flask import Blueprint, render_template, url_for, abort
from flask.ext.login import login_required, logout_user, current_user, login_user


user = Blueprint('users', __name__)


# the root of our website
@user.route('/')
@login_required
def index():
    return render_template("user/index.html")
