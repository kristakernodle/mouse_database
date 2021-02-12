import uuid

from sqlalchemy.dialects.postgresql import UUID

from .super_classes import Base
from ..extensions import db


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