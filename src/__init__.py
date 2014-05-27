from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import config

app = Flask(config.APP_NAME)
app.debug = True
app.config.from_object(config)
db = SQLAlchemy(app, session_options = {'expire_on_commit': False})
