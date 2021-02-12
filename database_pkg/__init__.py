from flask import Flask
from .extensions import db
from .utilities import Date
from .Models.pasta_handling_scores import PastaHandlingScores
from .Models.grooming_bouts import GroomingBout
from .Models.grooming_summary import GroomingSummary
from .Models.sr_trial_scores import SRTrialScore
from .Models.blind_trials import BlindTrial
from .Models.trials import Trial
from .Models.blind_folders import BlindFolder
from .Models.folders import Folder
from .Models.sessions import Session
from .Models.participant_details import ParticipantDetail
from .Models.reviewers import Reviewer
from .Models.experiments import Experiment
from .Models.mice import Mouse
from config import config


def create_app():
    app = Flask('database_pkg')
    app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    register_extensions(app)
    return app


def register_extensions(app):
    db.init_app(app)
    return None


app = create_app()
app.app_context().push()




