from flask import Flask
from .extensions import db
from .utilities import Date
from .Models import (PastaHandlingScores,
                     GroomingBout,
                     GroomingSummary,
                     SRTrialScore,
                     BlindTrial,
                     Trial,
                     BlindFolder,
                     Folder,
                     Session,
                     ParticipantDetail,
                     Reviewer,
                     Mouse,
                     Experiment,
                     SkilledReaching,
                     Grooming,
                     PastaHandling)
from config import config


def create_app():
    new_app = Flask('database_pkg')
    new_app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URI']
    new_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    register_extensions(new_app)
    return new_app


def register_extensions(new_app):
    db.init_app(new_app)
    return None


app = create_app()
app.app_context().push()




