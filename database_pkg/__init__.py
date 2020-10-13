from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config

DATABASE_URI = config['DATABASE_URI']
app = Flask('database_pkg')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from .utilities import Date
from .models import Mouse, Reviewer, Experiment, ParticipantDetail
import database_pkg.crud as crud
