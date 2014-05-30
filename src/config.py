import os
import common

#db_dir = "/tmp/"
db_dir = common.script_dir
basedir = common.script_dir
sqlite_db = 'sqlite:///' + os.path.join(db_dir, 'gnuclicker.db')

APP_NAME = "gnuclickers"
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', sqlite_db)
SQLALCHEMY_MIGRATE_REPO = os.path.join(common.script_dir, 'db_repository')
