import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pandas import read_csv

from .super_classes import Base
from ..extensions import db
from ..utilities import parse_date


class Mouse(Base):
    __tablename__ = 'mice'
    mouse_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    eartag = db.Column(db.Integer, nullable=False, unique=True)
    birthdate = db.Column(db.Date, nullable=False)
    genotype = db.Column(db.Boolean, nullable=False)
    sex = db.Column(db.String)

    participant_details = relationship("ParticipantDetail", backref="mice")

    def __repr__(self):
        return f"< Mouse {self.eartag} >"

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
        mouse_data_frame = read_csv(full_path,
                                    usecols=['mouse_id', 'eartag', 'birthdate', 'genotype', 'sex'],
                                    delimiter=',',
                                    dtype={'mouse_id': str, 'eartag': str, 'birthdate': str, 'genotype': str,
                                           'sex': str}
                                    )
        mouse_data_frame.genotype = mouse_data_frame.genotype.apply(lambda x: x == 'TRUE' or x == 'true')
        mouse_data_frame.birthdate = mouse_data_frame.birthdate.apply(lambda x: parse_date(x))
        for index, mouse_row in mouse_data_frame.iterrows():
            if cls.query.get(mouse_row["mouse_id"]) is None:
                Mouse(mouse_id=mouse_row["mouse_id"],
                      eartag=int(mouse_row["eartag"]),
                      birthdate=mouse_row["birthdate"],
                      genotype=mouse_row["genotype"],
                      sex=mouse_row["sex"]).add_to_db()
