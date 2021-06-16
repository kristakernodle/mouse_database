import uuid

from sqlalchemy.dialects.postgresql import UUID

from ..super_classes import Base
from ...extensions import db


class GroomingChain(Base):
    __tablename__ = 'grooming_chains'

    grooming_chain_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    grooming_bout_id = db.Column(UUID(as_uuid=True), db.ForeignKey('grooming_bouts.grooming_bout_id'))
    grooming_trial_id = db.Column(UUID(as_uuid=True), db.ForeignKey('grooming_trials.grooming_trial_id'),
                                    nullable=False)
    chain_string = db.Column(db.String, nullable=False)
    start_frame = db.Column(db.Integer, nullable=False)
    end_frame = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.SmallInteger, nullable=True)
    complete = db.Column(db.Boolean, nullable=True)
    grooming_phase_1 = db.Column(db.SmallInteger, nullable=True)
    grooming_phase_2 = db.Column(db.SmallInteger, nullable=True)
    grooming_phase_3 = db.Column(db.SmallInteger, nullable=True)
    grooming_phase_4 = db.Column(db.SmallInteger, nullable=True)
    num_transitions = db.Column(db.SmallInteger, nullable=True)
    num_atypical_transitions = db.Column(db.SmallInteger, nullable=True)
    num_skips = db.Column(db.SmallInteger, nullable=True)
    num_reverse = db.Column(db.SmallInteger, nullable=True)
    num_aborted = db.Column(db.SmallInteger, nullable=True)

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)
