import database_pkg as dpk
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from pathlib import Path
from database_pkg.utilities import check_if_sharedx_connected

db = dpk.db


class Mouse(db.Model):
    __tablename__ = 'mice'
    mouse_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    eartag = db.Column(db.Integer, nullable=False, unique=True)
    birthdate = db.Column(db.Date, nullable=False)
    genotype = db.Column(db.Boolean, nullable=False)
    sex = db.Column(db.String)

    participant_details = relationship("ParticipantDetail", backref="mice")

    def __repr__(self):
        return f"< Mouse {self.eartag} >"


class Experiment(db.Model):
    __tablename__ = 'experiments'
    experiment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    experiment_dir = db.Column(db.String, nullable=False, unique=True)
    experiment_name = db.Column(db.String, nullable=False, unique=True)

    session_re = db.Column(db.String, nullable=True)
    folder_re = db.Column(db.String, nullable=True)
    trial_re = db.Column(db.String, nullable=True)

    sessions = relationship("Session", backref="experiments")
    participants = relationship("ParticipantDetail", backref="experiments")

    def __repr__(self):
        return f"< Experiment {self.experiment_name} >"


class Reviewer(db.Model):
    __tablename__ = 'reviewers'
    reviewer_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    toScore_dir = db.Column(db.String, nullable=False, unique=True)
    scored_dir = db.Column(db.String, nullable=False, unique=True)

    scored_folders = relationship("BlindFolder", backref="reviewers")


class ParticipantDetail(db.Model):
    __tablename__ = 'participant_details'
    detail_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    mouse_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mice.mouse_id'), nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiments.experiment_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    participant_dir = db.Column(db.String, nullable=False, unique=True)
    exp_spec_details = db.Column(db.JSON)


class Session(db.Model):
    __tablename__ = 'sessions'
    session_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    mouse_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mice.mouse_id'), nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiments.experiment_id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_dir = db.Column(db.String, nullable=False, unique=True)
    session_num = db.Column(db.Integer, nullable=False)

    folders = relationship("Folder", backref="sessions")
    trials = relationship("Trial", backref="sessions")


class Folder(db.Model):
    __tablename__ = 'folders'
    folder_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    folder_dir = db.Column(db.String, nullable=False, unique=True)
    original_video = db.Column(db.String, nullable=True, unique=True)
    trial_frame_number_file = db.Column(db.String, nullable=False, unique=True)

    trials = relationship("Trial", backref="folders")
    score_folders = relationship("BlindFolder", backref="folders")


class BlindFolder(db.Model):
    __tablename__ = 'blind_folders'
    blind_folder_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('folders.folder_id'), nullable=False)
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reviewers.reviewer_id'), nullable=False)
    blind_name = db.Column(db.String, nullable=False, unique=True)

    blind_trials = relationship("BlindTrial", backref="blind_folders")

    def as_dict(self):
        return {
            'blind_folder_id': str(self.blind_folder_id),
            'folder_id': str(self.folder_id),
            'reviewer_id': str(self.reviewer_id),
            'blind_name': self.blind_name
        }

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def add_blind_trials(self, scored_blind_folder_path=None):
        if scored_blind_folder_path is None:
            reviewer = Reviewer.query.filter(Reviewer.reviewer_id == self.reviewer_id).first()
            scored_blind_folder_path = Path(reviewer.scored_dir).joinpath(
                f"{self.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")
        dpk.crud.add_blind_trials_from_scored_blind_folder(scored_blind_folder_path)

    def is_scored(self):
        if not check_if_sharedx_connected:
            return False
        reviewer = Reviewer.query.filter(Reviewer.reviewer_id == self.reviewer_id).first()
        scored_file_path = Path(reviewer.scored_dir).joinpath(
            f"{self.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")
        return scored_file_path.exists()


class Trial(db.Model):
    __tablename__ = 'trials'
    trial_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiments.experiment_id'), nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('folders.folder_id'), nullable=False)
    trial_dir = db.Column(db.String, nullable=False, unique=True)
    trial_date = db.Column(db.Date, nullable=False)
    trial_num = db.Column(db.Integer, nullable=False)

    scores = relationship("SRTrialScore", backref='trials')


class BlindTrial(db.Model):
    __tablename__ = 'blind_trials'
    blind_trial_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    blind_folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('blind_folders.blind_folder_id'))
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reviewers.reviewer_id'), nullable=False)
    trial_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trials.trial_id'), nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('folders.folder_id'), nullable=False)
    blind_trial_num = db.Column(db.Integer, nullable=False)

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()


class SRTrialScore(db.Model):
    __tablename__ = 'sr_trial_scores'
    trial_score_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    trial_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trials.trial_id'), nullable=False, unique=False)
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reviewers.reviewer_id'), nullable=False, unique=False)
    reach_score = db.Column(db.Integer, nullable=False, unique=False)
    abnormal_movt_score = db.Column(db.Boolean, nullable=False, unique=False)
    grooming_score = db.Column(db.Boolean, nullable=False, unique=False)
