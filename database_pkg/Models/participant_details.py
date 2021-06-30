import json
import uuid

import pandas as pd
from sqlalchemy.dialects.postgresql import UUID

from .super_classes import Base
from ..extensions import db
from ..utilities import Date, parse_date


class ParticipantDetail(Base):
    __tablename__ = 'participant_details'
    detail_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    mouse_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mice.mouse_id'), nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiments.experiment_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    participant_dir = db.Column(db.String, nullable=False, unique=True)
    exp_spec_details = db.Column(db.JSON)

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
        participant_details_df = pd.read_csv(full_path,
                                             usecols=['detail_id', 'mouse_id', 'experiment_id', 'start_date',
                                                      'end_date',
                                                      'participant_dir', 'exp_spec_details'],
                                             delimiter=',',
                                             dtype={'detail_id': str, 'mouse_id': str, 'experiment_id': str,
                                                    'start_date': str,
                                                    'end_date': str, 'participant_dir': str, 'exp_spec_details': str})
        participant_details_df.start_date = participant_details_df.start_date.apply(lambda x: parse_date(x))
        participant_details_df.end_date = participant_details_df.end_date.apply(lambda x: parse_date(x))

        for index, detail_row in participant_details_df.iterrows():
            if cls.query.get(detail_row["detail_id"]) is None:

                if type(detail_row["exp_spec_details"]) is not str:
                    exp_spec_details = None
                else:
                    exp_spec_details = json.loads(detail_row["exp_spec_details"])

                ParticipantDetail(detail_id=detail_row["detail_id"],
                                  mouse_id=detail_row["mouse_id"],
                                  experiment_id=detail_row["experiment_id"],
                                  start_date=Date.as_date(detail_row["start_date"]),
                                  end_date=Date.as_date(detail_row["end_date"]),
                                  participant_dir=detail_row["participant_dir"],
                                  exp_spec_details=exp_spec_details).add_to_db()
