import uuid

import pandas as pd
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .super_classes import Base
from ..extensions import db


class Experiment(Base):
    __tablename__ = 'experiments'
    experiment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    experiment_dir = db.Column(db.String, nullable=False, unique=True)
    experiment_type = db.Column(db.String, nullable=False)
    experiment_name = db.Column(db.String, nullable=False, unique=True)
    session_re = db.Column(db.String, nullable=True)
    __mapper_args__ = {'polymorphic_on': experiment_type}

    participants = relationship("ParticipantDetail", backref="experiments")
    sessions = relationship("Session", backref="experiments")

    def __repr__(self):
        return f"< Experiment {self.experiment_name} >"

    @classmethod
    def get_by_name(cls, experiment_name):
        return cls.query.filter_by(experiment_name=experiment_name).first()

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)

    def sessions_df(self):
        return pd.DataFrame.from_records([session.as_dict() for session in self.sessions])

    def participants_df(self):
        return pd.DataFrame.from_records([participant.as_dict() for participant in self.participants])

    @classmethod
    def reinstate(cls, full_path):
        experiments_data_frame = pd.read_csv(full_path, delimiter=',',
                                             dtype={'experiment_id': str, 'experiment_dir': str, 'experiment_name': str,
                                                    'session_re': str, 'folder_re': str, 'trial_re': str})
        for index, experiment_row in experiments_data_frame.iterrows():
            if cls.query.get(experiment_row["experiment_id"]) is None:
                Experiment(experiment_id=experiment_row["experiment_id"],
                           experiment_dir=experiment_row["experiment_dir"],
                           experiment_type=experiment_row["experiment_type"],
                           experiment_name=experiment_row["experiment_name"],
                           session_re=experiment_row["session_re"],
                           folder_re=experiment_row["folder_re"],
                           trial_re=experiment_row["trial_re"]).add_to_db()


class SkilledReaching(Experiment):
    # __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': 'skilled-reaching'}

    folder_re = db.Column(db.String, nullable=True)
    trial_re = db.Column(db.String, nullable=True)

    folders = relationship("Folder",
                           secondary="join(Session, Folder, Session.session_id == Folder.session_id)",
                           primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, Session.session_id==Folder.session_id)",
                           secondaryjoin="Session.session_id == Folder.session_id")

    def blind_folders(self):
        all_blind_folders = list()
        for folder in self.folders:
            all_blind_folders.extend(folder.score_folders)
        return all_blind_folders


class Grooming(Experiment):
    # __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': 'grooming'}

    scored_grooming = relationship("GroomingSummary",
                                   secondary="join(Session, GroomingSummary, Session.session_id == GroomingSummary.session_id)",
                                   primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, "
                                               "Session.session_id == GroomingSummary.session_id)",
                                   secondaryjoin="Session.session_id == GroomingSummary.session_id")

    grooming_bouts = relationship("GroomingBout",
                                  secondary="join(Session, GroomingBout, Session.session_id == GroomingBout.session_id)",
                                  primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, Session.session_id == GroomingBout.session_id)",
                                  secondaryjoin="Session.session_id == GroomingBout.session_id")


class PastaHandling(Experiment):
    # __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': 'pasta-handling'}

    scored_pasta_handling = relationship("PastaHandlingScores",
                                         secondary="join(Session, PastaHandlingScores, "
                                                   "Session.session_id == PastaHandlingScores.session_id)",
                                         primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, "
                                                     "Session.session_id == PastaHandlingScores.session_id)",
                                         secondaryjoin="Session.session_id == PastaHandlingScores.session_id")
