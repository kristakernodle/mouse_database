import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pandas import read_csv

from ..super_classes import Base
from ...extensions import db
from ...utilities import convert_dict_keys_to_str, merge_dicts


class GroomingBout(Base):
    __tablename__ = 'grooming_bouts'

    grooming_bout_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    grooming_trial_id = db.Column(UUID(as_uuid=True), db.ForeignKey('grooming_trials.grooming_trial_id'),
                                    nullable=False)
    bout_string = db.Column(db.String, nullable=False)
    start_frame = db.Column(db.Integer, nullable=True)
    end_frame = db.Column(db.Integer, nullable=True)
    bout_length = db.Column(db.Float, nullable=True)
    num_chains = db.Column(db.SmallInteger, nullable=False)
    num_complete_chains = db.Column(db.SmallInteger, nullable=False)

    chains = relationship("GroomingChain", backref='grooming_bouts')

    def is_same(self, new_bout):
        return all([self.grooming_trial_id == new_bout.grooming_trial_id,
                    self.bout_string == new_bout.bout_string,
                    self.start_frame == new_bout.start_frame,
                    self.end_frame == new_bout.end_frame,
                    self.bout_length == new_bout.bout_length,
                    self.num_chains == new_bout.chains_perMin,
                    self.num_complete_chains == new_bout.num_complete_chains])

    # def __init__(self, grooming_summary_id, session_id, bout_string, bout_start, bout_end,
    #              grooming_bout_id=None, interrupted=None, complete=None, chains_perMin=None, total_num_transitions=None,
    #              num_incorrect_transitions=None, correct_transitions=None, aborted_transitions=None,
    #              skipped_transitions=None, reversed_transitions=None, initiation_incorrect_transitions=None):
    #
    #     # Set values provided to init function
    #     self.grooming_summary_id = grooming_summary_id
    #     self.session_id = session_id
    #     self.bout_string = bout_string.replace('--', '-')
    #
    #     self.start_frame, self.end_frame = list(map(int, [bout_start, bout_end]))
    #
    #     if grooming_bout_id is None:
    #         # Calculate the number of chains (use this to set self.interrupted)
    #         temp_chain_strings = self.bout_string.strip('0').split('0')
    #         chain_strings = list()
    #         for temp_str in temp_chain_strings:
    #             if temp_str.startswith('-') and temp_str.endswith('-'):
    #                 chain_strings.append(f"0{temp_str}0")
    #             elif temp_str.startswith('-'):
    #                 chain_strings.append(f"0{temp_str}-0")
    #             elif temp_str.endswith('-'):
    #                 chain_strings.append(f"0-{temp_str}0")
    #             else:
    #                 chain_strings.append(f"0-{temp_str}-0")
    #
    #         self.chains_perMin = len(chain_strings)
    #
    #         self.interrupted = False
    #         if self.chains_perMin > 1:
    #             self.interrupted = True
    #
    #         # Perform transition analysis of self.bout_string
    #         correct_transitions = {(0, 1): 0,
    #                                (1, 2): 0,
    #                                (2, 3): 0,
    #                                (3, 4): 0,
    #                                (4, 5): 0,
    #                                (5, 0): 0}
    #
    #         aborted_transitions = dict()
    #         skipped_transitions = dict()
    #         reversed_transitions = dict()
    #         initiation_incorrect_transitions = dict()
    #         try:
    #             bout_tup = tuple(map(int, self.bout_string.strip('-').split('-')))
    #         except ValueError:
    #             breakpoint()
    #         bout_transition_tup = tuple([(bout_tup[idx], bout_tup[idx + 1]) for idx in range(len(bout_tup) - 1)])
    #         for transition in bout_transition_tup:
    #             if transition in correct_transitions.keys():
    #                 # Correct transitions
    #                 correct_transitions[transition] = correct_transitions.get(transition, 0) + 1
    #             elif transition in list(zip([0] * 4, range(2, 6))):
    #                 # Transitions with incorrect initiation
    #                 initiation_incorrect_transitions[transition] = initiation_incorrect_transitions.get(transition,
    #                                                                                                     0) + 1
    #             elif transition in list(zip(range(1, 5), [0] * 4)):
    #                 # Aborted transitions (premature termination)
    #                 aborted_transitions[transition] = aborted_transitions.get(transition, 0) + 1
    #             elif (transition[0] - transition[1]) > 0:
    #                 # Reversed transitions
    #                 reversed_transitions[transition] = reversed_transitions.get(transition, 0) + 1
    #             elif (transition[0] - transition[1]) < 0:
    #                 # Skipped transitions
    #                 skipped_transitions[transition] = skipped_transitions.get(transition, 0) + 1
    #             elif transition[0] == transition[1]:
    #                 # No transition
    #                 continue
    #             else:
    #                 breakpoint()
    #
    #         # Set all values related to transitions
    #         self.complete = all([item != 0 for item in correct_transitions.values()])
    #         self.num_incorrect_transitions = len(initiation_incorrect_transitions) + len(aborted_transitions) + \
    #                                          len(reversed_transitions) + len(skipped_transitions)
    #         self.total_num_transitions = self.num_incorrect_transitions + sum(correct_transitions.values())
    #         self.correct_transitions = convert_dict_keys_to_str(correct_transitions)
    #         self.aborted_transitions = convert_dict_keys_to_str(aborted_transitions)
    #         self.skipped_transitions = convert_dict_keys_to_str(skipped_transitions)
    #         self.reversed_transitions = convert_dict_keys_to_str(reversed_transitions)
    #         self.initiation_incorrect_transitions = convert_dict_keys_to_str(initiation_incorrect_transitions)
    #
    #     else:
    #         self.grooming_bout_id = grooming_bout_id
    #         self.interrupted = interrupted
    #         self.complete = complete
    #         self.chains_perMin = chains_perMin
    #         self.total_num_transitions = total_num_transitions
    #         self.num_incorrect_transitions = num_incorrect_transitions
    #         self.correct_transitions = correct_transitions
    #         self.aborted_transitions = aborted_transitions
    #         self.skipped_transitions = skipped_transitions
    #         self.reversed_transitions = reversed_transitions
    #         self.initiation_incorrect_transitions = initiation_incorrect_transitions

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
        # TODO: rewrite GroomingBout.reinstate()
        pass
        # grooming_bout_df = read_csv(full_path,
        #                             usecols=['grooming_bout_id', 'grooming_summary_id', 'session_id',
        #                                      'bout_string', 'start_frame', 'end_frame', 'interrupted', 'complete',
        #                                      'chains_perMin', 'total_num_transitions', 'num_incorrect_transitions',
        #                                      'correct_transitions', 'aborted_transitions', 'skipped_transitions',
        #                                      'reversed_transitions', 'initiation_incorrect_transitions'],
        #                             delimiter=',',
        #                             dtype={'grooming_bout_id': str,
        #                                    'grooming_summary_id': str,
        #                                    'session_id': str,
        #                                    'bout_string': str,
        #                                    'start_frame': int,
        #                                    'end_frame': int,
        #                                    'interrupted': bool,
        #                                    'complete': bool,
        #                                    'chains_perMin': int,
        #                                    'total_num_transitions': int,
        #                                    'num_incorrect_transitions': str,
        #                                    'correct_transitions': str,
        #                                    'aborted_transitions': str,
        #                                    'skipped_transitions': str,
        #                                    'reversed_transitions': str,
        #                                    'initiation_incorrect_transitions': str})
        # for index, grooming_bout_row in grooming_bout_df.iterrows():
        #     if cls.query.get(grooming_bout_row['grooming_summary_id']) is None:
        #         GroomingBout(grooming_bout_id=grooming_bout_row['grooming_bout_id'],
        #                      grooming_summary_id=grooming_bout_row['grooming_summary_id'],
        #                      session_id=grooming_bout_row['session_id'],
        #                      bout_string=grooming_bout_row['bout_string'],
        #                      bout_start=grooming_bout_row['start_frame'],
        #                      bout_end=grooming_bout_row['end_frame'],
        #                      interrupted=grooming_bout_row['interrupted'],
        #                      complete=grooming_bout_row['complete'],
        #                      chains_perMin=grooming_bout_row['chains_perMin'],
        #                      total_num_transitions=grooming_bout_row['total_num_transitions'],
        #                      num_incorrect_transitions=grooming_bout_row['num_incorrect_transitions'],
        #                      correct_transitions=grooming_bout_row['correct_transitions'],
        #                      aborted_transitions=grooming_bout_row['aborted_transitions'],
        #                      skipped_transitions=grooming_bout_row['skipped_transitions'],
        #                      reversed_transitions=grooming_bout_row['reversed_transitions'],
        #                      initiation_incorrect_transitions=grooming_bout_row[
        #                          'initiation_incorrect_transitions']).add_to_db()

    @classmethod
    def update_from_dirs(cls):
        # TODO: write GroomingBout.update_from_dirs() if needed
        pass
