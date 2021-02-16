import uuid

from sqlalchemy.dialects.postgresql import UUID
from pandas import read_csv

from ..super_classes import Base
from ...extensions import db


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

    @classmethod
    def reinstate(cls, full_path):
        pasta_handling_scores_df = read_csv(full_path,
                                               usecols=['pasta_handling_score_id', 'session_id', 'scored_session_dir',
                                                        'trial_num', 'time_to_eat', 'grasp_paw_start',
                                                        'guide_paw_start',
                                                        'left_forepaw_adjustments', 'right_forepaw_adjustments',
                                                        'left_forepaw_failure_to_contact',
                                                        'right_forepaw_failure_to_contact',
                                                        'guide_grasp_switch', 'drops', 'mouth_pulling',
                                                        'pasta_long_paws_together', 'pasta_short_paws_apart',
                                                        'abnormal_posture', 'iron_grip', 'guide_around_grasp',
                                                        'angling_with_head_tilt'],
                                               delimiter=',',
                                               dtype={'pasta_handling_score_id': str, 'session_id': str,
                                                      'scored_session_dir': str, 'trial_num': int, 'time_to_eat': float,
                                                      'grasp_paw_start': str, 'guide_paw_start': str,
                                                      'left_forepaw_adjustments': int, 'right_forepaw_adjustments': int,
                                                      'left_forepaw_failure_to_contact': int,
                                                      'right_forepaw_failure_to_contact': int,
                                                      'guide_grasp_switch': int, 'drops': int, 'mouth_pulling': int,
                                                      'pasta_long_paws_together': int, 'pasta_short_paws_apart': int,
                                                      'abnormal_posture': int, 'iron_grip': int,
                                                      'guide_around_grasp': int,
                                                      'angling_with_head_tilt': int})
        for index, ph_row in pasta_handling_scores_df.iterrows():
            if cls.query.get(ph_row['pasta_handling_score_id']) is None:
                PastaHandlingScores(pasta_handling_score_id=ph_row['pasta_handling_score_id'],
                                    session_id=ph_row['session_id'],
                                    scored_session_dir=ph_row['scored_session_dir'],
                                    trial_num=ph_row['trial_num'],
                                    time_to_eat=ph_row['time_to_eat'],
                                    grasp_paw_start=ph_row['grasp_paw_start'],
                                    guide_paw_start=ph_row['guide_paw_start'],
                                    left_forepaw_adjustments=ph_row['left_forepaw_adjustments'],
                                    right_forepaw_adjustments=ph_row['right_forepaw_adjustments'],
                                    left_forepaw_failure_to_contact=ph_row['left_forepaw_failure_to_contact'],
                                    right_forepaw_failure_to_contact=ph_row['right_forepaw_failure_to_contact'],
                                    guide_grasp_switch=ph_row['guide_grasp_switch'],
                                    drops=ph_row['drops'],
                                    mouth_pulling=ph_row['mouth_pulling'],
                                    pasta_long_paws_together=ph_row['pasta_long_paws_together'],
                                    pasta_short_paws_apart=ph_row['pasta_short_paws_apart'],
                                    abnormal_posture=ph_row['abnormal_posture'],
                                    iron_grip=ph_row['iron_grip'],
                                    guide_around_grasp=ph_row['guide_around_grasp'],
                                    angling_with_head_tilt=ph_row['angling_with_head_tilt']).add_to_db()
