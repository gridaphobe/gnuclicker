import os
import common

#db_dir = "/tmp/"
db_dir = common.script_dir
basedir = common.script_dir

APP_NAME = "gnuclickers"
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(db_dir, 'gnuclicker.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(common.script_dir, 'db_repository')
