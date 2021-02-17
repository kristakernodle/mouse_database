import uuid
from pathlib import Path

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pandas import read_csv

from .super_classes import Base
from ..extensions import db
from ..utilities import parse_date


class Session(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        db.UniqueConstraint('experiment_id', 'session_dir'),
    )
    session_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    mouse_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mice.mouse_id'), nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiments.experiment_id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_dir = db.Column(db.String, nullable=False, unique=True)
    session_num = db.Column(db.Integer, nullable=False)

    folders = relationship("Folder", backref="sessions")
    trials = relationship("Trial", backref="sessions")

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
        sessions_data_frame = read_csv(full_path,
                                       usecols=['session_id', 'mouse_id', 'experiment_id', 'session_date',
                                                'session_dir',
                                                'session_num'],
                                       delimiter=',',
                                       dtype={'session_id': str, 'mouse_id': str, 'experiment_id': str,
                                              'session_date': str, 'session_dir': str, 'session_num': int}
                                       )
        sessions_data_frame.session_date = sessions_data_frame.session_date.apply(lambda x: parse_date(x))
        for index, session_row in sessions_data_frame.iterrows():
            if cls.query.get(session_row['session_id']) is None:
                Session(session_id=session_row['session_id'],
                        mouse_id=session_row['mouse_id'],
                        experiment_id=session_row['experiment_id'],
                        session_date=session_row['session_date'],
                        session_dir=session_row['session_dir'],
                        session_num=session_row['session_num']).add_to_db()

