import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .super_classes import Base
from ..extensions import db


class GroomingSummary(Base):
    __tablename__ = 'grooming_summary'
    __table_args__ = (
        db.UniqueConstraint('session_id', 'scored_session_dir', 'trial_num'),
    )
    grooming_summary_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True,
                                    nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    scored_session_dir = db.Column(db.String, nullable=False)
    trial_num = db.Column(db.SmallInteger, nullable=False)
    trial_length = db.Column(db.Float, nullable=False)
    latency_to_onset = db.Column(db.Float, nullable=False)
    num_bouts = db.Column(db.SmallInteger, nullable=False)
    total_time_grooming = db.Column(db.Float, nullable=False)
    num_interrupted_bouts = db.Column(db.SmallInteger, nullable=False)
    num_chains = db.Column(db.SmallInteger, nullable=False)
    num_complete_chains = db.Column(db.SmallInteger, nullable=False)
    avg_time_per_bout = db.Column(db.Float, nullable=False)

    bouts = relationship("GroomingBout", backref='grooming_summary')

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)