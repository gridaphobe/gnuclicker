from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required

class LoginForm(Form):
  universityId = TextField('University ID', validators = [Required()])
  password = PasswordField('Password')
