import database_pkg as dpk
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
import sqlalchemy
import uuid
from pathlib import Path
from database_pkg.utilities import check_if_sharedx_connected, random_string_generator
import pandas as pd

db = dpk.db


class Base(db.Model):
    __abstract__ = True

    def add_to_db(self, my_object):
        db.session.add(my_object)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    def as_dict(self, my_object):
        return {key: value for key, value in sqlalchemy.inspect(my_object).dict.items() if '_sa_' not in key}

    def remove_from_db(self, my_object):
        db.session.delete(my_object)
        try:
            db.session.commit()
        except:
            db.session.rollback()


class Mouse(Base):
    __tablename__ = 'mice'
    mouse_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    eartag = db.Column(db.Integer, nullable=False, unique=True)
    birthdate = db.Column(db.Date, nullable=False)
    genotype = db.Column(db.Boolean, nullable=False)
    sex = db.Column(db.String)

    participant_details = relationship("ParticipantDetail", backref="mice")

    def __repr__(self):
        return f"< Mouse {self.eartag} >"

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)


class Experiment(Base):
    __tablename__ = 'experiments'
    experiment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    experiment_dir = db.Column(db.String, nullable=False, unique=True)
    experiment_name = db.Column(db.String, nullable=False, unique=True)

    session_re = db.Column(db.String, nullable=True)
    folder_re = db.Column(db.String, nullable=True)
    trial_re = db.Column(db.String, nullable=True)

    participants = relationship("ParticipantDetail", backref="experiments")
    sessions = relationship("Session", backref="experiments")
    folders = relationship("Folder",
                           secondary="join(Session, Folder, Session.session_id == Folder.session_id)",
                           primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, "
                                       "Session.session_id==Folder.session_id)",
                           secondaryjoin="Session.session_id == Folder.session_id")
    scored_grooming = relationship("GroomingSummary",
                                   secondary="join(Session, GroomingSummary, Session.session_id == GroomingSummary.session_id)",
                                   primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, "
                                               "Session.session_id == GroomingSummary.session_id)",
                                   secondaryjoin="Session.session_id == GroomingSummary.session_id")

    scored_pasta_handling = relationship("PastaHandlingScores",
                                         secondary="join(Session, PastaHandlingScores, "
                                                   "Session.session_id == PastaHandlingScores.session_id)",
                                         primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, "
                                                   "Session.session_id == PastaHandlingScores.session_id)",
                                         secondaryjoin="Session.session_id == PastaHandlingScores.session_id")

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

    def blind_folders(self):
        all_blind_folders = list()
        for folder in self.folders:
            all_blind_folders.extend(folder.score_folders)
        return all_blind_folders


class Reviewer(Base):
    __tablename__ = 'reviewers'
    reviewer_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    toScore_dir = db.Column(db.String, nullable=False, unique=True)
    scored_dir = db.Column(db.String, nullable=False, unique=True)

    scored_folders = relationship("BlindFolder", backref="reviewers")

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)


class ParticipantDetail(Base):
    __tablename__ = 'participant_details'
    detail_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    mouse_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mice.mouse_id'), nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiments.experiment_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    participant_dir = db.Column(db.String, nullable=False, unique=True)
    exp_spec_details = db.Column(db.JSON)

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)


class Session(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        db.UniqueConstraint('experiment_id', 'session_dir'),
    )
    session_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    mouse_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mice.mouse_id'), nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiments.experiment_id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_dir = db.Column(db.String, nullable=False, unique=True)
    session_num = db.Column(db.Integer, nullable=False)

    folders = relationship("Folder", backref="sessions")
    trials = relationship("Trial", backref="sessions")

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)


class Folder(Base):
    __tablename__ = 'folders'
    folder_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    folder_dir = db.Column(db.String, nullable=False, unique=True)
    original_video = db.Column(db.String, nullable=True, unique=True)
    trial_frame_number_file = db.Column(db.String, nullable=False, unique=True)

    trials = relationship("Trial", backref="folders")
    score_folders = relationship("BlindFolder", backref="folders")

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)

    def create_blind_folder(self, reviewer):
        blind_name = random_string_generator()
        while BlindFolder.query.filter_by(blind_name=blind_name).first() is not None:
            blind_name = random_string_generator()

        blind_folder = BlindFolder(folder_id=self.folder_id, reviewer_id=reviewer.reviewer_id, blind_name=blind_name)
        blind_folder.add_to_db()

        all_blind_trial_nums = set(range(1, len(self.trials)+1))
        for trial in self.trials:
            trial.create_blind_trial(blind_folder, all_blind_trial_nums.pop())

        return blind_folder


class BlindFolder(Base):
    __tablename__ = 'blind_folders'
    __table_args__ = (
        db.UniqueConstraint('folder_id', 'reviewer_id'),
    )
    blind_folder_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('folders.folder_id'), nullable=False)
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reviewers.reviewer_id'), nullable=False)
    blind_name = db.Column(db.String, nullable=False, unique=True)

    blind_trials = relationship("BlindTrial", backref="blind_folders")

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)

    def is_scored(self):
        if not check_if_sharedx_connected:
            return False
        reviewer = Reviewer.query.get(self.reviewer_id)
        scored_file_path = Path(reviewer.scored_dir).joinpath(
            f"{self.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")
        return scored_file_path.exists()


class Trial(Base):
    __tablename__ = 'trials'
    trial_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiments.experiment_id'), nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('folders.folder_id'), nullable=False)
    trial_dir = db.Column(db.String, nullable=False, unique=True)
    trial_date = db.Column(db.Date, nullable=False)
    trial_num = db.Column(db.Integer, nullable=False)

    scores = relationship("SRTrialScore", backref='trials')

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)

    def create_blind_trial(self, blind_folder, blind_trial_num):
        blind_trial = BlindTrial(blind_folder_id=blind_folder.blind_folder_id, reviewer_id=blind_folder.reviewer_id,
                                 trial_id=self.trial_id, folder_id=self.folder_id, blind_trial_num=blind_trial_num)
        blind_trial.add_to_db()


class BlindTrial(Base):
    __tablename__ = 'blind_trials'
    blind_trial_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    blind_folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('blind_folders.blind_folder_id'))
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reviewers.reviewer_id'), nullable=False)
    trial_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trials.trial_id'), nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('folders.folder_id'), nullable=False)
    blind_trial_num = db.Column(db.Integer, nullable=False)

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)


class SRTrialScore(Base):
    __tablename__ = 'sr_trial_scores'
    __table_args__ = (
        db.UniqueConstraint('trial_id', 'reviewer_id'),
    )
    trial_score_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    trial_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trials.trial_id'), nullable=False, unique=False)
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reviewers.reviewer_id'), nullable=False, unique=False)
    reach_score = db.Column(db.Integer, nullable=False, unique=False)
    abnormal_movt_score = db.Column(db.Boolean, nullable=False, unique=False)
    grooming_score = db.Column(db.Boolean, nullable=False, unique=False)

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)


class GroomingSummary(Base):
    __tablename__ = 'grooming_summary'
    __table_args__ = (
        db.UniqueConstraint('session_id', 'scored_session_dir', 'trial_num'),
    )
    grooming_summary_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    scored_session_dir = db.Column(db.String, nullable=False)
    trial_num = db.Column(db.SmallInteger, nullable=False)
    trial_length = db.Column(db.Float, nullable=False)
    latency_to_onset = db.Column(db.Float, nullable=False)
    num_bouts = db.Column(db.SmallInteger, nullable=False)
    total_time_grooming = db.Column(db.Float, nullable=False)
    num_interrupted_bouts = db.Column(db.Float, nullable=False)
    num_chains = db.Column(db.SmallInteger, nullable=False)
    num_complete_chains = db.Column(db.SmallInteger, nullable=False)
    avg_time_per_bout = db.Column(db.Float, nullable=False)

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)


class PastaHandlingScores(Base):
    __tablename__ = 'pasta_handling_scores'
    pasta_handling_score_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    scored_session_dir = db.Column(db.String, nullable=False)
    trial_num = db.Column(db.SmallInteger, nullable=False)
    time_to_eat = db.Column(db.Float, nullable=False)
    grasp_paw_start = db.Column(db.String, nullable=False)
    guide_paw_start = db.Column(db.String, nullable=False)
    left_forepaw_adjustments = db.Column(db.Integer, nullable=False)
    right_forepaw_adjustments = db.Column(db.Integer, nullable=False)
    left_forepaw_failure_to_contact = db.Column(db.Integer, nullable=False)
    right_forepaw_failure_to_contact = db.Column(db.Integer, nullable=False)
    guide_grasp_switch = db.Column(db.Integer, nullable=False)
    drops = db.Column(db.Integer, nullable=False)
    mouth_pulling = db.Column(db.Integer, nullable=False)
    pasta_long_paws_together = db.Column(db.Boolean, nullable=False)
    pasta_short_paws_apart = db.Column(db.Boolean, nullable=False)
    abnormal_posture = db.Column(db.Boolean, nullable=False)
    iron_grip = db.Column(db.Boolean, nullable=False)
    guide_around_grasp = db.Column(db.Boolean, nullable=False)
    angling_with_head_tilt = db.Column(db.Boolean, nullable=False)

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)
