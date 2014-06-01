from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField, FieldList, FormField, HiddenField
from wtforms.validators import Required

class LoginForm(Form):
  universityId = TextField('University ID', validators = [Required()])
  password = PasswordField('Password')

class AnswerForm(Form):
  answer = TextField('Answer', validators=[Required()])
  correct = BooleanField()

class QuestionForm(Form):
  title = TextField('Title', validators=[Required()])
  prompt = TextField('Prompt', validators=[Required()])
  choices = FieldList(FormField(AnswerForm),min_entries=5)
