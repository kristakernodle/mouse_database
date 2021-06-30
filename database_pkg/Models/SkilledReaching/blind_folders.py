import uuid
from pathlib import Path

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pandas import read_csv

from ...utilities import check_if_sharedx_connected
from ...extensions import db
from ..super_classes import Base
from ..reviewers import Reviewer


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

    @classmethod
    def reinstate(cls, full_path):
        blind_folders_df = read_csv(full_path,
                                       usecols=['blind_folder_id', 'folder_id', 'reviewer_id', 'blind_name'],
                                       delimiter=',',
                                       dtype={'blind_folder_id': str, 'folder_id': str, 'reviewer_id': str,
                                              'blind_name': str}
                                       )
        for index, blind_folder_row in blind_folders_df.iterrows():
            if cls.query.get(blind_folder_row['blind_folder_id']) is None:
                BlindFolder(blind_folder_id=blind_folder_row['blind_folder_id'],
                            folder_id=blind_folder_row['folder_id'],
                            reviewer_id=blind_folder_row['reviewer_id'],
                            blind_name=blind_folder_row['blind_name']
                            ).add_to_db()
