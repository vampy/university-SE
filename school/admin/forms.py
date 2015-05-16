from flask_wtf import Form
from wtforms import PasswordField, SubmitField, ValidationError, StringField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email
from school.forms import RedirectForm
from flask.ext.login import current_user

class EditSemesterForm(Form):
    pass

class AddSemesterForm(Form):
    pass

class EditGroupForm(Form):
    pass

class AddGroupForm(Form):
    pass

class EditDepartmentForm(Form):
    pass

class AddDepartmentForm(Form):
    pass

class EditLanguageForm(Form):
    pass

class AddLanguageForm(Form):
    pass

# TODO maybe add teaches here?
