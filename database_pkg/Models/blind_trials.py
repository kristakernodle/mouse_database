import uuid

from sqlalchemy.dialects.postgresql import UUID

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