from flask.ext.login import login_required, current_user
from flask import Blueprint, render_template, flash, redirect, url_for, request
from school.decorators import role_required
from school.config import FLASH_SUCCESS, FLASH_ERROR
from school.models import *
from school.user import User

admin = Blueprint('admin', __name__)

@admin.route("/semesters")
@login_required
@role_required(admin=True)
def semesters():
    return "TODO"

# TODO add all the other views
