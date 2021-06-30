import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import pandas as pd

from ..super_classes import Base
from ...extensions import db


class GroomingTrial(Base):
    __tablename__ = 'grooming_trials'
    __table_args__ = (
                      db.UniqueConstraint('session_id', 'scored_session_dir', 'trial_num'),
                     )

    grooming_trial_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True,
                                  nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    scored_session_dir = db.Column(db.String, nullable=False)
    trial_num = db.Column(db.SmallInteger, nullable=False)
    trial_length = db.Column(db.Float, nullable=True)
    total_time_grooming = db.Column(db.Float, nullable=True)
    latency_to_onset = db.Column(db.Float, nullable=True)
    num_bouts = db.Column(db.SmallInteger, nullable=False)
    num_chains = db.Column(db.SmallInteger, nullable=False)
    num_complete_chains = db.Column(db.SmallInteger, nullable=False)

    bouts = relationship("GroomingBout", backref='grooming_trials')
    chains = relationship("GroomingChain", backref='grooming_trials')

    def data_equal(self, other_trial):
        return all([self.num_bouts == other_trial.num_bouts,
                    self.num_chains == other_trial.chains_perMin,
                    self.num_complete_chains == other_trial.num_complete_chains])

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
        # TODO rewrite: GroomingTrial.reinstate()
        pass
        # grooming_summary_df = pd.read_csv(full_path,
        #                                   usecols=['grooming_summary_id', 'session_id', 'scored_session_dir',
        #                                            'trial_num',
        #                                            'trial_length', 'latency_to_onset', 'num_bouts',
        #                                            'total_time_grooming',
        #                                            'num_interrupted_bouts', 'chains_perMin', 'num_complete_chains',
        #                                            'avg_time_per_bout'],
        #                                   delimiter=',',
        #                                   dtype={'grooming_summary_id': str, 'session_id': str,
        #                                          'scored_session_dir': str,
        #                                          'trial_num': int, 'trial_length': float, 'latency_to_onset': float,
        #                                          'num_bouts': int, 'total_time_grooming': float,
        #                                          'num_interrupted_bouts': int, 'chains_perMin': int,
        #                                          'num_complete_chains': int, 'avg_time_per_bout': float})
        # for index, grooming_summary_row in grooming_summary_df.iterrows():
        #     if cls.query.get(grooming_summary_row['grooming_summary_id']) is None:
        #         GroomingTrial(grooming_summary_id=grooming_summary_row['grooming_summary_id'],
        #                       session_id=grooming_summary_row['session_id'],
        #                       scored_session_dir=grooming_summary_row['scored_session_dir'],
        #                       trial_num=grooming_summary_row['trial_num'],
        #                       trial_length=grooming_summary_row['trial_length'],
        #                       latency_to_onset=grooming_summary_row['latency_to_onset'],
        #                       num_bouts=grooming_summary_row['num_bouts'],
        #                       total_time_grooming=grooming_summary_row['total_time_grooming'],
        #                       num_interrupted_bouts=grooming_summary_row['num_interrupted_bouts'],
        #                       chains_perMin=grooming_summary_row['chains_perMin'],
        #                       num_complete_chains=grooming_summary_row['num_complete_chains'],
        #                       avg_time_per_bout=grooming_summary_row['avg_time_per_bout']).add_to_db()

    def update_from_bouts(self):
        # TODO: rewrite/delete/replace GroomingTrial.update_from_bouts()
        pass
        # all_bouts_df = pd.DataFrame.from_records([bout.as_dict() for bout in self.bouts])
        #
        # try:
        #     all_bouts_df['total_frames'] = all_bouts_df['end_frame'] - all_bouts_df['start_frame']
        # except KeyError:
        #     return
        #
        # num_bouts = len(all_bouts_df)
        #
        # complete_count_dict = all_bouts_df.complete.value_counts().sort_index().reset_index().transpose().to_dict()
        # complete_count = 0
        # incomplete_count = 0
        # for key, value in complete_count_dict.items():
        #     if value['index']:
        #         complete_count = value['complete']
        #     elif not value['index']:
        #         incomplete_count = value['complete']
        # chains_perMin = incomplete_count + complete_count
        # num_complete_chains = complete_count
        #
        # interrupted_count_dict = all_bouts_df.interrupted.value_counts().sort_index().reset_index().transpose().to_dict()
        #
        # interrupted_count = 0
        # for key, value in interrupted_count_dict.items():
        #     if value['index']:
        #         interrupted_count = value['interrupted']
        #
        # num_interrupted_bouts = interrupted_count
        #
        # all_grooming_frames = all_bouts_df.total_frames.sum()
        # total_time_grooming = all_grooming_frames / 100
        #
        # if not self.data_equal(num_bouts, total_time_grooming, num_interrupted_bouts, chains_perMin, num_complete_chains):
        #     self.num_bouts = num_bouts
        #     self.total_time_grooming = total_time_grooming
        #     self.num_interrupted_bouts = num_interrupted_bouts
        #     self.chains_perMin = chains_perMin
        #     self.num_complete_chains = num_complete_chains
        #     self.update()


