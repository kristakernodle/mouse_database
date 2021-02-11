import database_pkg as dpkg
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
import sqlalchemy
import uuid
from pathlib import Path
from database_pkg.utilities import check_if_sharedx_connected, random_string_generator, convert_dict_keys_to_str
import pandas as pd

db = dpkg.db


class Base(db.Model):
    __abstract__ = True

    def add_to_db(self, my_object):
        db.session.add(my_object)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    def as_dict(self, my_object):
        return {key: value for key, value in sqlalchemy.inspect(my_object).dict.items() if '_sa_' not in key}

    def remove_from_db(self, my_object):
        db.session.delete(my_object)
        try:
            db.session.commit()
        except:
            db.session.rollback()


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


class Experiment(Base):
    __tablename__ = 'experiments'
    experiment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    experiment_dir = db.Column(db.String, nullable=False, unique=True)
    experiment_name = db.Column(db.String, nullable=False, unique=True)

    session_re = db.Column(db.String, nullable=True)
    folder_re = db.Column(db.String, nullable=True)
    trial_re = db.Column(db.String, nullable=True)

    participants = relationship("ParticipantDetail", backref="experiments")
    sessions = relationship("Session", backref="experiments")

    folders = relationship("Folder",
                           secondary="join(Session, Folder, Session.session_id == Folder.session_id)",
                           primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, Session.session_id==Folder.session_id)",
                           secondaryjoin="Session.session_id == Folder.session_id")

    grooming_bouts = relationship("GroomingBout",
                                  secondary="join(Session, GroomingBout, Session.session_id == GroomingBout.session_id)",
                                  primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, Session.session_id == GroomingBout.session_id)",
                                  secondaryjoin="Session.session_id == GroomingBout.session_id")

    scored_grooming = relationship("GroomingSummary",
                                   secondary="join(Session, GroomingSummary, Session.session_id == GroomingSummary.session_id)",
                                   primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, Session.session_id == GroomingSummary.session_id)",
                                   secondaryjoin="Session.session_id == GroomingSummary.session_id")

    scored_pasta_handling = relationship("PastaHandlingScores",
                                         secondary="join(Session, PastaHandlingScores, Session.session_id == PastaHandlingScores.session_id)",
                                         primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, Session.session_id == PastaHandlingScores.session_id)",
                                         secondaryjoin="Session.session_id == PastaHandlingScores.session_id")

    def __repr__(self):
        return f"< Experiment {self.experiment_name} >"

    @classmethod
    def get_by_name(cls, experiment_name):
        return cls.query.filter_by(experiment_name=experiment_name).first()

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)

    def sessions_df(self):
        return pd.DataFrame.from_records([session.as_dict() for session in self.sessions])

    def participants_df(self):
        return pd.DataFrame.from_records([participant.as_dict() for participant in self.participants])

    def blind_folders(self):
        all_blind_folders = list()
        for folder in self.folders:
            all_blind_folders.extend(folder.score_folders)
        return all_blind_folders


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


class Folder(Base):
    __tablename__ = 'folders'
    folder_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    folder_dir = db.Column(db.String, nullable=False, unique=True)
    original_video = db.Column(db.String, nullable=True, unique=True)
    trial_frame_number_file = db.Column(db.String, nullable=False, unique=True)

    trials = relationship("Trial", backref="folders")
    score_folders = relationship("BlindFolder", backref="folders")

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)

    def create_blind_folder(self, reviewer):
        blind_name = random_string_generator()
        while BlindFolder.query.filter_by(blind_name=blind_name).first() is not None:
            blind_name = random_string_generator()

        blind_folder = BlindFolder(folder_id=self.folder_id, reviewer_id=reviewer.reviewer_id, blind_name=blind_name)
        blind_folder.add_to_db()

        all_blind_trial_nums = set(range(1, len(self.trials) + 1))
        for trial in self.trials:
            trial.create_blind_trial(blind_folder, all_blind_trial_nums.pop())

        return blind_folder


class BlindFolder(Base):
    __tablename__ = 'blind_folders'
    __table_args__ = (
        db.UniqueConstraint('folder_id', 'reviewer_id'),
    )
    blind_folder_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('folders.folder_id'), nullable=False)
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reviewers.reviewer_id'), nullable=False)
    blind_name = db.Column(db.String, nullable=False, unique=True)

    blind_trials = relationship("BlindTrial", backref="blind_folders")

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)

    def is_scored(self):
        if not check_if_sharedx_connected:
            return False
        reviewer = Reviewer.query.get(self.reviewer_id)
        scored_file_path = Path(reviewer.scored_dir).joinpath(
            f"{self.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")
        return scored_file_path.exists()


class Trial(Base):
    __tablename__ = 'trials'
    trial_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    experiment_id = db.Column(UUID(as_uuid=True), db.ForeignKey('experiments.experiment_id'), nullable=False)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('sessions.session_id'), nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('folders.folder_id'), nullable=False)
    trial_dir = db.Column(db.String, nullable=False, unique=True)
    trial_date = db.Column(db.Date, nullable=False)
    trial_num = db.Column(db.Integer, nullable=False)

    scores = relationship("SRTrialScore", backref='trials')

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)

    def create_blind_trial(self, blind_folder, blind_trial_num):
        blind_trial = BlindTrial(blind_folder_id=blind_folder.blind_folder_id, reviewer_id=blind_folder.reviewer_id,
                                 trial_id=self.trial_id, folder_id=self.folder_id, blind_trial_num=blind_trial_num)
        blind_trial.add_to_db()


class BlindTrial(Base):
    __tablename__ = 'blind_trials'
    blind_trial_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    blind_folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('blind_folders.blind_folder_id'))
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reviewers.reviewer_id'), nullable=False)
    trial_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trials.trial_id'), nullable=False)
    folder_id = db.Column(UUID(as_uuid=True), db.ForeignKey('folders.folder_id'), nullable=False)
    blind_trial_num = db.Column(db.Integer, nullable=False)

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)


class SRTrialScore(Base):
    __tablename__ = 'sr_trial_scores'
    __table_args__ = (
        db.UniqueConstraint('trial_id', 'reviewer_id'),
    )
    trial_score_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    trial_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trials.trial_id'), nullable=False, unique=False)
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('reviewers.reviewer_id'), nullable=False, unique=False)
    reach_score = db.Column(db.Integer, nullable=False, unique=False)
    abnormal_movt_score = db.Column(db.Boolean, nullable=False, unique=False)
    grooming_score = db.Column(db.Boolean, nullable=False, unique=False)

    def add_to_db(self, my_object=None):
        super().add_to_db(my_object=self)

    def as_dict(self, my_object=None):
        if my_object is None:
            my_object = self
        return super().as_dict(my_object)

    def remove_from_db(self, my_object=None):
        super().remove_from_db(my_object=self)


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

    # def analyze_bout_to_chains(self):
    #     temp_chain_strings = self.bout_string.strip('0').split('0')
    #     chain_strings = list()
    #     for temp_str in temp_chain_strings:
    #         if temp_str.startswith('-') and temp_str.endswith('-'):
    #             chain_strings.append(f"0{temp_str}0")
    #         elif temp_str.startswith('-'):
    #             chain_strings.append(f"0{temp_str}-0")
    #         elif temp_str.endswith('-'):
    #             chain_strings.append(f"0-{temp_str}0")
    #         else:
    #             chain_strings.append(f"0-{temp_str}-0")
    #
    #     for chain_str in chain_strings:
    #         correct_transitions = {(0, 1): 0,
    #                                (1, 2): 0,
    #                                (2, 3): 0,
    #                                (3, 4): 0,
    #                                (4, 5): 0,
    #                                (5, 0): 0}
    #         aborted_transitions = dict()
    #         skipped_transitions = dict()
    #         reversed_transitions = dict()
    #         initiation_incorrect_transitions = dict()
    #         try:
    #             chain_tup = tuple(map(int, chain_str.split('-')))
    #         except ValueError:
    #             if chain_str == '0- -0':
    #                 continue
    #             print(chain_str)
    #         chain_transition_tup = tuple([(chain_tup[idx], chain_tup[idx + 1]) for idx in range(len(chain_tup) - 1)])
    #         for transition in chain_transition_tup:
    #             if transition == (4, 30):
    #                 print('where is this coming from?')
    #             elif transition in correct_transitions.keys():
    #                 # Correct transitions
    #                 correct_transitions[transition] = correct_transitions.get(transition, 0) + 1
    #             elif transition in list(zip([0] * 4, range(2, 6))):
    #                 # Transitions with incorrect initiation
    #                 initiation_incorrect_transitions[transition] = initiation_incorrect_transitions.get(transition, 0) + 1
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
    #                 continue
    #             else:
    #                 print('what is this transition')
    #
    #         num_incorrect_transitions = len(initiation_incorrect_transitions) + \
    #                                     len(aborted_transitions) + \
    #                                     len(reversed_transitions) + \
    #                                     len(skipped_transitions)
    #         total_num_transitions = num_incorrect_transitions + sum(correct_transitions.values())
    #
    #         GroomingBoutChain(grooming_bout_id=self.grooming_bout_id,
    #                           grooming_summary_id=self.grooming_summary_id,
    #                           total_num_transitions=total_num_transitions,
    #                           num_incorrect_transitions=num_incorrect_transitions,
    #                           correct_transitions=convert_dict_keys_to_str(correct_transitions),
    #                           aborted_transitions=convert_dict_keys_to_str(aborted_transitions),
    #                           skipped_transitions=convert_dict_keys_to_str(skipped_transitions),
    #                           reversed_transitions=convert_dict_keys_to_str(reversed_transitions),
    #                           initiation_incorrect_transitions=convert_dict_keys_to_str(initiation_incorrect_transitions)
    #                           ).add_to_db()
#
#
# class GroomingBoutChain(Base):
#     __tablename__ = 'grooming_bout_chains'
#     chain_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
#     grooming_bout_id = db.Column(UUID(as_uuid=True), db.ForeignKey('grooming_bouts.grooming_bout_id'), nullable=False)
#     grooming_summary_id = db.Column(UUID(as_uuid=True), db.ForeignKey('grooming_summary.grooming_summary_id'),
#                                     nullable=False)
#     total_num_transitions = db.Column(db.SmallInteger, nullable=False)
#     num_incorrect_transitions = db.Column(db.SmallInteger, nullable=False)
#     correct_transitions = db.Column(db.JSON, nullable=False)
#     aborted_transitions = db.Column(db.JSON, nullable=False)
#     skipped_transitions = db.Column(db.JSON, nullable=False)
#     reversed_transitions = db.Column(db.JSON, nullable=False)
#     initiation_incorrect_transitions = db.Column(db.JSON, nullable=False)
#
#     def add_to_db(self, my_object=None):
#         super().add_to_db(my_object=self)
#
#     def as_dict(self, my_object=None):
#         if my_object is None:
#             my_object = self
#         return super().as_dict(my_object)
#
#     def remove_from_db(self, my_object=None):
#         super().remove_from_db(my_object=self)


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
