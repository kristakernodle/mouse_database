import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pandas import read_csv

from ..super_classes import Base
from ...extensions import db


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

    @classmethod
    def reinstate(cls, full_path):
        grooming_summary_df = read_csv(full_path,
                                          usecols=['grooming_summary_id', 'session_id', 'scored_session_dir',
                                                   'trial_num',
                                                   'trial_length', 'latency_to_onset', 'num_bouts',
                                                   'total_time_grooming',
                                                   'num_interrupted_bouts', 'num_chains', 'num_complete_chains',
                                                   'avg_time_per_bout'],
                                          delimiter=',',
                                          dtype={'grooming_summary_id': str, 'session_id': str,
                                                 'scored_session_dir': str,
                                                 'trial_num': int, 'trial_length': float, 'latency_to_onset': float,
                                                 'num_bouts': int, 'total_time_grooming': float,
                                                 'num_interrupted_bouts': int, 'num_chains': int,
                                                 'num_complete_chains': int, 'avg_time_per_bout': float})
        for index, grooming_summary_row in grooming_summary_df.iterrows():
            if cls.query.get(grooming_summary_row['grooming_summary_id']) is None:
                GroomingSummary(grooming_summary_id=grooming_summary_row['grooming_summary_id'],
                                session_id=grooming_summary_row['session_id'],
                                scored_session_dir=grooming_summary_row['scored_session_dir'],
                                trial_num=grooming_summary_row['trial_num'],
                                trial_length=grooming_summary_row['trial_length'],
                                latency_to_onset=grooming_summary_row['latency_to_onset'],
                                num_bouts=grooming_summary_row['num_bouts'],
                                total_time_grooming=grooming_summary_row['total_time_grooming'],
                                num_interrupted_bouts=grooming_summary_row['num_interrupted_bouts'],
                                num_chains=grooming_summary_row['num_chains'],
                                num_complete_chains=grooming_summary_row['num_complete_chains'],
                                avg_time_per_bout=grooming_summary_row['avg_time_per_bout']).add_to_db()
