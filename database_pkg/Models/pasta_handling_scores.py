import uuid

from sqlalchemy.dialects.postgresql import UUID

from .super_classes import Base
from ..extensions import db


class PastaHandlingScores(Base):
    __tablename__ = 'pasta_handling_scores'
    pasta_handling_score_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True,
                                        nullable=False)
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