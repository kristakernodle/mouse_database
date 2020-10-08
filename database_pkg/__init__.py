
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config
import database_pkg.models as models

DATABASE_URI = config['DATABASE_URI']


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)


