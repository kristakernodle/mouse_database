import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pandas import read_csv

from .super_classes import Base
from ..extensions import db


class Reviewer(Base):
    __tablename__ = 'reviewers'
    reviewer_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    toScore_dir = db.Column(db.String, nullable=False, unique=True)
    scored_dir = db.Column(db.String, nullable=False, unique=True)

    scored_folders = relationship("BlindFolder", backref="reviewers")

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)

    @classmethod
    def get_by_name(cls, first_name, last_name):
        return cls.query.filter_by(first_name=first_name, last_name=last_name).first()

    @classmethod
    def reinstate(cls, full_path):
        reviewer_data_frame = read_csv(full_path,
                                       usecols=['reviewer_id', 'first_name', 'last_name', 'toScore_dir',
                                                'scored_dir'],
                                       delimiter=',',
                                       dtype={'reviewer_id': str, 'first_name': str,
                                              'last_name': str, 'toScore_dir': str,
                                              'scored_dir': str})
        for index, reviewer_row in reviewer_data_frame.iterrows():
            if cls.query.get(reviewer_row["reviewer_id"]) is None:
                Reviewer(reviewer_id=reviewer_row["reviewer_id"],
                         first_name=reviewer_row["first_name"],
                         last_name=reviewer_row["last_name"],
                         toScore_dir=reviewer_row["toScore_dir"],
                         scored_dir=reviewer_row["scored_dir"]).add_to_db()
