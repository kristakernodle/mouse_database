import uuid
from pathlib import Path

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pandas import read_csv

from ..SkilledReaching.trials import Trial
from ..SkilledReaching.blind_folders import BlindFolder
from ..super_classes import Base
from ...extensions import db
from ...utilities import random_string_generator


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

        BlindFolder(folder_id=self.folder_id, reviewer_id=reviewer.reviewer_id, blind_name=blind_name).add_to_db()

        blind_folder = BlindFolder.query.filter_by(blind_name=blind_name).first()

        all_blind_trial_nums = set(range(1, len(self.trials) + 1))
        for trial in self.trials:
            trial.create_blind_trial(blind_folder, all_blind_trial_nums.pop())

        return blind_folder

    @classmethod
    def reinstate(cls, full_path):
        folders_data_frame = read_csv(full_path,
                                         usecols=['folder_id', 'session_id', 'folder_dir', 'original_video',
                                                  'trial_frame_number_file'],
                                         delimiter=',',
                                         dtype={'folder_id': str, 'session_id': str, 'folder_dir': str,
                                                'original_video': str, 'trial_frame_number_file': str}
                                         )
        for index, folder_row in folders_data_frame.iterrows():
            if cls.query.get(folder_row['folder_id']) is None:
                Folder(folder_id=folder_row['folder_id'],
                       session_id=folder_row['session_id'],
                       folder_dir=folder_row['folder_dir'],
                       original_video=folder_row['original_video'],
                       trial_frame_number_file=folder_row['trial_frame_number_file']).add_to_db()

    def add_trials_from_dir(self, experiment_trial_re, session):
        all_trials = Path(self.folder_dir).glob(f'{experiment_trial_re}')
        for trial_dir in all_trials:
            trial = Trial.query.filter_by(trial_dir=str(trial_dir)).first()
            if trial is None:
                trial_name = trial_dir.stem
                trial_num = trial_name.split('_')[-1].strip('RTG')
                Trial(experiment_id=session.experiment_id,
                      session_id=self.session_id,
                      folder_id=self.folder_id,
                      trial_dir=str(trial_dir),
                      trial_date=session.session_date,
                      trial_num=int(trial_num)).add_to_db()
