from flask import Blueprint, render_template, url_for, abort

frontend = Blueprint('frontend', __name__)


# the root of our website
@frontend.route('/', methods=["GET"])
def index():
    return render_template('frontend/index.html')


@frontend.route('/login', methods=["POST"])
def login():
    abort(401)