import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pandas import read_csv

from ..super_classes import Base
from ..SkilledReaching.blind_trials import BlindTrial
from ...extensions import db
from ...utilities import parse_date


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

    @classmethod
    def reinstate(cls, full_path):
        trials_data_frame = read_csv(full_path,
                                        usecols=['trial_id', 'experiment_id', 'session_id', 'folder_id', 'trial_dir',
                                                 'trial_date', 'trial_num'],
                                        delimiter=',',
                                        dtype={'trial_id': str, 'experiment_id': str, 'session_id': str,
                                               'folder_id': str,
                                               'trial_dir': str, 'trial_date': str, 'trial_num': int}
                                        )
        trials_data_frame.trial_date = trials_data_frame.trial_date.apply(lambda x: parse_date(x))
        for index, trial_row in trials_data_frame.iterrows():
            if cls.query.get(trial_row['trial_id']) is None:
                Trial(trial_id=trial_row['trial_id'],
                      experiment_id=trial_row['experiment_id'],
                      session_id=trial_row['session_id'],
                      folder_id=trial_row['folder_id'],
                      trial_dir=trial_row['trial_dir'],
                      trial_date=trial_row['trial_date'],
                      trial_num=trial_row['trial_num']).add_to_db()
