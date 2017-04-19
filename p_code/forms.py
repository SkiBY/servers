from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required

class LoginForm(Form):
    login = TextField('login', validators = [Required()])
    password = TextField('password', validators = [Required()])