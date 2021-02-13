import uuid

from sqlalchemy.dialects.postgresql import UUID
from pandas import read_csv

from ..extensions import db
from .super_classes import Base


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

    @classmethod
    def reinstate(cls, full_path):
        blind_trials_df = read_csv(full_path,
                                      usecols=['blind_trial_id', 'blind_folder_id', 'reviewer_id', 'trial_id',
                                               'folder_id',
                                               'blind_trial_num'],
                                      delimiter=',',
                                      dtype={'blind_trial_id': str, 'blind_folder_id': str, 'reviewer_id': str,
                                             'trial_id': str, 'folder_id': str, 'blind_trial_num': int}
                                      )
        for index, blind_trial_row in blind_trials_df.iterrows():
            if cls.query.get(blind_trial_row['blind_trial_id']) is None:
                BlindTrial(blind_trial_id=blind_trial_row['blind_trial_id'],
                           blind_folder_id=blind_trial_row['blind_folder_id'],
                           reviewer_id=blind_trial_row['reviewer_id'],
                           trial_id=blind_trial_row['trial_id'],
                           folder_id=blind_trial_row['folder_id'],
                           blind_trial_num=blind_trial_row['blind_trial_num']).add_to_db()
