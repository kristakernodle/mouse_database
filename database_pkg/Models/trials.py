import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .super_classes import Base
from .blind_trials import BlindTrial
from ..extensions import db


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