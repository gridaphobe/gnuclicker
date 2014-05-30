from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import config

app = Flask(config.APP_NAME)
app.debug = True
app.config.from_object(config)

# la la la i don't know why we need this
# but it's needed for sessions somehow
app.secret_key = "uhf981uior;u12io;br1;2ofyo;12ufp;1i2jd"

db = SQLAlchemy(app, session_options = {'expire_on_commit': False})
lm = LoginManager()
lm.init_app(app)
