import uuid

from sqlalchemy.dialects.postgresql import UUID

from .super_classes import Base
from ..extensions import db
from ..utilities import convert_dict_keys_to_str


class GroomingBout(Base):
    __tablename__ = 'grooming_bouts'
    grooming_bout_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    grooming_summary_id = db.Column(UUID(as_uuid=True), db.ForeignKey('grooming_summary.grooming_summary_id'),
                                    nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    bout_string = db.Column(db.String, nullable=False)
    bout_start = db.Column(db.Integer, nullable=False)
    bout_end = db.Column(db.Integer, nullable=False)
    interrupted = db.Column(db.Boolean, nullable=False)
    complete = db.Column(db.Boolean, nullable=False)
    num_chains = db.Column(db.SmallInteger, nullable=False)
    total_num_transitions = db.Column(db.SmallInteger, nullable=False)
    num_incorrect_transitions = db.Column(db.SmallInteger, nullable=False)
    correct_transitions = db.Column(db.JSON, nullable=False)
    aborted_transitions = db.Column(db.JSON, nullable=False)
    skipped_transitions = db.Column(db.JSON, nullable=False)
    reversed_transitions = db.Column(db.JSON, nullable=False)
    initiation_incorrect_transitions = db.Column(db.JSON, nullable=False)

    # chains = relationship("GroomingBoutChain", backref='grooming_bouts')

    def __init__(self, grooming_summary_id, session_id, bout_string, bout_start, bout_end):
        # Set values provided to init function
        self.grooming_summary_id = grooming_summary_id
        self.session_id = session_id
        self.bout_string = bout_string.replace('--', '-')

        self.bout_start, self.bout_end = list(map(int, [bout_start, bout_end]))

        # Calculate the number of chains (use this to set self.interrupted)
        temp_chain_strings = self.bout_string.strip('0').split('0')
        chain_strings = list()
        for temp_str in temp_chain_strings:
            if temp_str.startswith('-') and temp_str.endswith('-'):
                chain_strings.append(f"0{temp_str}0")
            elif temp_str.startswith('-'):
                chain_strings.append(f"0{temp_str}-0")
            elif temp_str.endswith('-'):
                chain_strings.append(f"0-{temp_str}0")
            else:
                chain_strings.append(f"0-{temp_str}-0")

        self.num_chains = len(chain_strings)

        self.interrupted = False
        if self.num_chains > 1:
            self.interrupted = True

        # Perform transition analysis of self.bout_string
        correct_transitions = {(0, 1): 0,
                               (1, 2): 0,
                               (2, 3): 0,
                               (3, 4): 0,
                               (4, 5): 0,
                               (5, 0): 0}
        aborted_transitions = dict()
        skipped_transitions = dict()
        reversed_transitions = dict()
        initiation_incorrect_transitions = dict()
        try:
            bout_tup = tuple(map(int, self.bout_string.strip('-').split('-')))
        except ValueError:
            breakpoint()
        bout_transition_tup = tuple([(bout_tup[idx], bout_tup[idx + 1]) for idx in range(len(bout_tup) - 1)])
        for transition in bout_transition_tup:
            if transition in correct_transitions.keys():
                # Correct transitions
                correct_transitions[transition] = correct_transitions.get(transition, 0) + 1
            elif transition in list(zip([0] * 4, range(2, 6))):
                # Transitions with incorrect initiation
                initiation_incorrect_transitions[transition] = initiation_incorrect_transitions.get(transition, 0) + 1
            elif transition in list(zip(range(1, 5), [0] * 4)):
                # Aborted transitions (premature termination)
                aborted_transitions[transition] = aborted_transitions.get(transition, 0) + 1
            elif (transition[0] - transition[1]) > 0:
                # Reversed transitions
                reversed_transitions[transition] = reversed_transitions.get(transition, 0) + 1
            elif (transition[0] - transition[1]) < 0:
                # Skipped transitions
                skipped_transitions[transition] = skipped_transitions.get(transition, 0) + 1
            elif transition[0] == transition[1]:
                # No transition
                continue
            else:
                breakpoint()

        # Set all values related to transitions
        self.complete = all([item != 0 for item in correct_transitions.values()])
        self.num_incorrect_transitions = len(initiation_incorrect_transitions) + len(aborted_transitions) + \
                                         len(reversed_transitions) + len(skipped_transitions)
        self.total_num_transitions = self.num_incorrect_transitions + sum(correct_transitions.values())
        self.correct_transitions = convert_dict_keys_to_str(correct_transitions)
        self.aborted_transitions = convert_dict_keys_to_str(aborted_transitions)
        self.skipped_transitions = convert_dict_keys_to_str(skipped_transitions)
        self.reversed_transitions = convert_dict_keys_to_str(reversed_transitions)
        self.initiation_incorrect_transitions = convert_dict_keys_to_str(initiation_incorrect_transitions)

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
        # TODO grooming_bouts from back up file
        pass