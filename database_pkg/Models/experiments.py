import shutil
import uuid
from math import isnan
from pathlib import Path

import pandas as pd
from pandas.errors import ParserError
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import exists, and_
from typing import List

from .mice import Mouse
from .participant_details import ParticipantDetail
from .reviewers import Reviewer
from .sessions import Session, ChatSapSession
from .SkilledReaching import Folder, Trial, BlindFolder, BlindTrial, SRTrialScore
from .Grooming import GroomingTrial, GroomingBout, GroomingChain
from .PastaHandling import PastaHandlingScores
from .super_classes import Base
from ..utilities import get_original_video_and_frame_number_file, Date
from ..extensions import db


class Experiment(Base):
    __tablename__ = 'experiments'
    experiment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    experiment_dir = db.Column(db.String, nullable=False, unique=True)
    experiment_name = db.Column(db.String, nullable=False, unique=True)
    session_re = db.Column(db.String, nullable=True)
    __mapper_args__ = {'polymorphic_on': experiment_name}

    participants = relationship("ParticipantDetail", backref="experiments")
    sessions: List[Session] = relationship("Session", backref="experiments")

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
        # noinspection PyTypeChecker
        return pd.DataFrame.from_records([session.as_dict() for session in self.sessions])

    def participants_df(self):
        # noinspection PyTypeChecker
        return pd.DataFrame.from_records([participant.as_dict() for participant in self.participants])

    def _update_sessions(self):
        if not Path(self.experiment_dir).exists():
            print(f'Experiment directory does not exist: {self.experiment_dir}')

        # noinspection PyTypeChecker
        # doesn't check self.participants is iterable
        for participant in self.participants:

            sessions_search_dir = Path(participant.participant_dir)
            if len(self.session_re.split('/')) > 1:
                for item in self.session_re.split('/')[:-1]:
                    sessions_search_dir = sessions_search_dir.joinpath(item)

            sessions_in_dir = list(str(session) for session in
                                   list(sessions_search_dir.glob(f'{self.session_re.split("/")[-1]}')))

            for session_dir in sessions_in_dir:
                session = Session.query.filter_by(session_dir=str(session_dir)).first()
                if session is None:
                    session_name = Path(session_dir).name

                    if self.experiment_name in ['dlxCKO-pasta-handling', 'dyt1-skilled-reaching']:
                        et_eartag, session_date, session_num = session_name.split('_')
                    else:
                        et_eartag, session_date, calibration_num, session_num = session_name.split('_')

                    Session(mouse_id=participant.mouse_id,
                            experiment_id=self.experiment_id,
                            session_date=Date.as_date(session_date),
                            session_dir=session_dir,
                            session_num=int(session_num.strip('T-MISNGDA'))).add_to_db()

    @classmethod
    def reinstate(cls, full_path):
        experiments_data_frame = pd.read_csv(full_path, delimiter=',',
                                             dtype={'experiment_id': str, 'experiment_dir': str, 'experiment_name': str,
                                                    'session_re': str, 'folder_re': str, 'trial_re': str,
                                                    'experiment_phase': str})
        for index, experiment_row in experiments_data_frame.iterrows():
            if cls.query.get(experiment_row["experiment_id"]) is None:
                if experiment_row["experiment_name"] == 'dlxCKO-skilled-reaching':
                    DlxSkilledReaching(experiment_id=experiment_row["experiment_id"],
                                       experiment_dir=experiment_row["experiment_dir"],
                                       experiment_name=experiment_row["experiment_name"],
                                       session_re=experiment_row["session_re"],
                                       folder_re=experiment_row["folder_re"],
                                       trial_re=experiment_row["trial_re"]).add_to_db()
                elif experiment_row["experiment_name"] == 'dlxCKO-grooming':
                    DlxGrooming(experiment_id=experiment_row["experiment_id"],
                                experiment_dir=experiment_row["experiment_dir"],
                                experiment_name=experiment_row["experiment_name"],
                                session_re=experiment_row["session_re"]).add_to_db()
                elif experiment_row["experiment_name"] == 'dlxCKO-pasta-handling':
                    DlxPastaHandling(experiment_id=experiment_row["experiment_id"],
                                     experiment_dir=experiment_row["experiment_dir"],
                                     experiment_name=experiment_row["experiment_name"],
                                     session_re=experiment_row["session_re"]).add_to_db()
                elif experiment_row["experiment_name"] == 'dyt1-skilled-reaching':
                    DYT1SkilledReaching(experiment_id=experiment_row["experiment_id"],
                                        experiment_dir=experiment_row["experiment_dir"],
                                        experiment_name=experiment_row["experiment_name"],
                                        session_re=experiment_row["session_re"],
                                        folder_re=experiment_row["folder_re"],
                                        trial_re=experiment_row["trial_re"]).add_to_db()
                elif experiment_row["experiment_name"] == 'dlxCKO-chatSap-skilled-reaching':
                    DlxChatSapSkilledReaching(experiment_id=experiment_row["experiment_id"],
                                              experiment_dir=experiment_row["experiment_dir"],
                                              experiment_name=experiment_row["experiment_name"],
                                              session_re=experiment_row["session_re"],
                                              folder_re=experiment_row["folder_re"],
                                              trial_re=experiment_row["trial_re"],
                                              experiment_phase=experiment_row["experiment_phase"]).add_to_db()


class DlxSkilledReaching(Experiment):
    __mapper_args__ = {'polymorphic_identity': 'dlxCKO-skilled-reaching'}

    folder_re = db.Column(db.String, nullable=True)
    trial_re = db.Column(db.String, nullable=True)

    folders = relationship(
        "Folder",
        secondary="join(Session, Folder, Session.session_id == Folder.session_id)",
        primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, Session.session_id==Folder.session_id)",
        secondaryjoin="Session.session_id == Folder.session_id")

    def blind_folders(self):
        all_blind_folders = list()
        for folder in self.folders:
            # noinspection PyTypeChecker
            all_blind_folders.extend(folder.score_folders)
        return all_blind_folders

    def _update_folders(self):
        # noinspection PyTypeChecker
        # doesn't check self.sessions for iterable
        for session in self.sessions:
            all_folders = Path(session.session_dir).glob(f'{self.folder_re}')
            for folder_dir in all_folders:
                folder = Folder.query.filter_by(folder_dir=str(folder_dir)).first()
                if folder is None:
                    original_video, trial_frame_number_file = get_original_video_and_frame_number_file(self,
                                                                                                       session,
                                                                                                       folder_dir)
                    Folder(session_id=session.session_id,
                           folder_dir=str(folder_dir),
                           original_video=str(original_video),
                           trial_frame_number_file=str(trial_frame_number_file)).add_to_db()

    def _update_trials(self):
        for folder in self.folders:
            session = Session.query.get(folder.session_id)

            all_trials = Path(folder.folder_dir).glob(f'{self.trial_re}')
            for trial_dir in all_trials:
                trial = Trial.query.filter_by(trial_dir=str(trial_dir)).first()
                if trial is None:
                    trial_name = trial_dir.stem
                    trial_num = trial_name.split('_')[-1].strip('RTG')
                    Trial(experiment_id=self.experiment_id,
                          session_id=folder.session_id,
                          folder_id=folder.folder_id,
                          trial_dir=str(trial_dir),
                          trial_date=session.session_date,
                          trial_num=int(trial_num)).add_to_db()

    def _update_trial_scores(self):

        for folder in self.folders:
            # noinspection PyTypeChecker
            # doesn't check folder.score_folders is iterable
            for blind_folder in folder.score_folders:
                reviewer = Reviewer.query.get(blind_folder.reviewer_id)

                if all([item is not None for item in
                        [SRTrialScore.query.filter_by(
                            trial_id=blind_trial.trial_id,
                            reviewer_id=reviewer.reviewer_id).first()
                         for blind_trial in blind_folder.blind_trials]]):
                    continue

                else:

                    scored_blind_folder_path = Path(reviewer.scored_dir).joinpath(
                        f"{blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")

                    if scored_blind_folder_path.exists():
                        try:
                            all_blind_folder_scores = pd.read_csv(
                                scored_blind_folder_path,
                                usecols=['Trial', 'Score', 'Movement', 'Grooming'],
                                delimiter=',',
                                dtype={'Trial': float, 'Score': float, 'Movement': str, 'Grooming': str}
                            )
                        except ValueError:
                            try:
                                all_blind_folder_scores = pd.read_csv(
                                    scored_blind_folder_path,
                                    usecols=['Trial', 'Score', 'Movement', 'Grooming '],
                                    delimiter=',',
                                    dtype={'Trial': float, 'Score': float, 'Movement': str, 'Grooming ': str}
                                )
                                all_blind_folder_scores['Grooming'] = all_blind_folder_scores['Grooming ']
                            except ValueError:
                                try:
                                    all_blind_folder_scores = pd.read_csv(
                                        scored_blind_folder_path,
                                        usecols=['Trial ', 'Score', 'Movement', 'Grooming'],
                                        delimiter=',',
                                        dtype={'Trial ': float, 'Score': float, 'Movement': str, 'Grooming': str}
                                    )
                                    all_blind_folder_scores['Trial'] = all_blind_folder_scores['Trial ']
                                except ValueError:
                                    print(f"For god's sake, reformat file {scored_blind_folder_path}")
                        except (ParserError, ValueError):
                            print(f"Reformat file {scored_blind_folder_path}")
                            shutil.move(str(scored_blind_folder_path), str(Path(reviewer.scored_dir).parent))
                            continue

                        for index, scored_row in all_blind_folder_scores.iterrows():

                            if isnan(scored_row['Trial']) or isnan(scored_row['Score']):
                                continue

                            blind_trial = BlindTrial.query.filter_by(blind_folder_id=blind_folder.blind_folder_id,
                                                                     reviewer_id=reviewer.reviewer_id,
                                                                     blind_trial_num=int(scored_row['Trial'])).first()

                            if blind_trial is None:
                                blind_trial_num = int(scored_row['Trial'])
                                trial = Trial.query.filter_by(folder_id=folder.folder_id,
                                                              trial_num=blind_trial_num).first()
                                if trial is None:
                                    print('Trial is none?')
                                    continue
                                blind_trial = BlindTrial(blind_folder_id=blind_folder.blind_folder_id,
                                                         reviewer_id=reviewer.reviewer_id,
                                                         trial_id=trial.trial_id,
                                                         folder_id=folder.folder_id,
                                                         blind_trial_num=blind_trial_num)
                                blind_trial.add_to_db()

                            if scored_row['Movement'] == '1':
                                movt = True
                            elif scored_row['Movement'] == '0':
                                movt = False
                            else:
                                movt = None

                            if scored_row['Grooming'] == '1':
                                groom = True
                            elif scored_row['Grooming'] == '0':
                                groom = False
                            else:
                                groom = None

                            trial_score = SRTrialScore.query.filter_by(trial_id=blind_trial.trial_id).filter_by(
                                reviewer_id=reviewer.reviewer_id).first()

                            if trial_score is None:
                                if groom is None:
                                    print('I guess we have to figure this out now')
                                SRTrialScore(trial_id=blind_trial.trial_id,
                                             reviewer_id=blind_trial.reviewer_id,
                                             reach_score=int(scored_row['Score']),
                                             abnormal_movt_score=movt,
                                             grooming_score=groom).add_to_db()
                            elif all([trial_score.reach_score == int(scored_row['Score']),
                                      trial_score.abnormal_movt_score == movt,
                                      trial_score.grooming_score == groom]):
                                continue
                            else:
                                trial_score.reach_score = int(scored_row['Score'])
                                trial_score.abnormal_movt_score = movt
                                trial_score.grooming_score = groom
                                trial_score.add_to_db()

                    else:
                        print(f"Not Scored: {str(scored_blind_folder_path)}")

    def update_from_dirs(self):
        self._update_sessions()
        self._update_folders()
        self._update_trials()
        self._update_trial_scores()

    def status_report(self):
        all_folders_not_blinded = Folder.query \
            .join(Session, Folder.session_id == Session.session_id) \
            .filter(Session.experiment_id == self.experiment_id) \
            .filter(~exists()
                    .where(and_(Folder.folder_id == BlindFolder.folder_id))) \
            .all()
        all_blind_folders_not_scored = BlindFolder.query \
            .join(Folder, BlindFolder.folder_id == Folder.folder_id) \
            .join(Session, Folder.session_id == Session.session_id) \
            .filter(Session.experiment_id == self.experiment_id) \
            .filter(~exists()
                    .where(and_(BlindFolder.folder_id == Trial.folder_id,
                                Trial.trial_id == SRTrialScore.trial_id))).all()
        print(f"Number Folders Not Blinded: {len(all_folders_not_blinded)}\n"
              f"Number of Blind Folders Not Scored: {len(all_blind_folders_not_scored)}\n")

    def get_all_scored_trials(self):
        all_scored_trials = pd.read_sql(
            db.session.query(Mouse.eartag,
                             Mouse.sex,
                             Mouse.birthdate,
                             Mouse.genotype,
                             Session.session_date,
                             Session.session_dir,
                             Session.session_num,
                             Experiment.experiment_name,
                             Trial.trial_dir,
                             Trial.trial_date,
                             Trial.trial_num,
                             Reviewer.first_name,
                             Reviewer.last_name,
                             SRTrialScore.reach_score,
                             SRTrialScore.grooming_score,
                             SRTrialScore.abnormal_movt_score) \
                .join(Session, Session.mouse_id == Mouse.mouse_id) \
                .join(Experiment, Experiment.experiment_id == Session.experiment_id) \
                .join(Trial, Trial.session_id == Session.session_id) \
                .join(SRTrialScore, SRTrialScore.trial_id == Trial.trial_id) \
                .join(Reviewer, Reviewer.reviewer_id == SRTrialScore.reviewer_id) \
                .statement,
            db.session.bind)

        all_scored_trials = all_scored_trials.loc[all_scored_trials['experiment_name'] == self.experiment_name]


        #
        # all_scored_trials_list = SRTrialScore.query.join(Trial, SRTrialScore.trial_id == Trial.trial_id).filter(
        #     Trial.experiment_id == self.experiment_id).all()
        # all_scored_trials_listdict = list()
        # for scored_trial in all_scored_trials_list:
        #     trial = Trial.query.get(scored_trial.trial_id)
        #     session = Session.query.get(trial.session_id)
        #     mouse = Mouse.query.get(session.mouse_id)
        #     reviewer = Reviewer.query.get(scored_trial.reviewer_id)
        #     all_scored_trials_listdict.append(
        #         {'eartag': mouse.eartag,
        #          'genotype': mouse.genotype,
        #          'birthdate': mouse.birthdate,
        #          'sex': mouse.sex,
        #          'session_dir': session.session_dir,
        #          'session_num': session.session_num,
        #          'session_date': session.session_date,
        #          'reviewer': f"{reviewer.first_name} {reviewer.last_name}",
        #          'trial_dir': trial.trial_dir,
        #          'reach_score': scored_trial.reach_score,
        #          'abnormal_movt_score': scored_trial.abnormal_movt_score,
        #          'grooming_score': scored_trial.grooming_score})
        return all_scored_trials


class DYT1SkilledReaching(DlxSkilledReaching):
    __mapper_args__ = {'polymorphic_identity': 'dyt1-skilled-reaching'}

    def _update_trial_scores(self):
        for folder in self.folders:
            # noinspection PyTypeChecker
            # doesn't check folder.score_folders is iterable
            for blind_folder in folder.score_folders:
                reviewer = Reviewer.query.get(blind_folder.reviewer_id)
                scored_blind_folder_path = Path(reviewer.scored_dir).joinpath(
                    f"{blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")

                if scored_blind_folder_path.exists():
                    try:
                        all_blind_folder_scores = pd.read_csv(
                            scored_blind_folder_path,
                            usecols=['Trial', 'Score'],
                            delimiter=',',
                            dtype={'Trial': float, 'Score': float}
                        )
                    except (ParserError, ValueError):
                        print(f"Reformat file {scored_blind_folder_path}")
                        shutil.move(str(scored_blind_folder_path), str(Path(reviewer.scored_dir).parent))
                        continue

                    for index, scored_row in all_blind_folder_scores.iterrows():
                        if isnan(scored_row['Trial']) or isnan(scored_row['Score']):
                            continue

                        blind_trial = BlindTrial.query.filter_by(blind_folder_id=blind_folder.blind_folder_id,
                                                                 blind_trial_num=int(scored_row['Trial'])).first()

                        if blind_trial is None:
                            blind_trial_num = int(scored_row['Trial'])
                            trial = Trial.query.filter_by(folder_id=folder.folder_id, trial_num=blind_trial_num).first()
                            if trial is None:
                                print('Trial is none?')
                                continue
                            blind_trial = BlindTrial(blind_folder_id=blind_folder.blind_folder_id,
                                                     reviewer_id=reviewer.reviewer_id,
                                                     trial_id=trial.trial_id,
                                                     folder_id=folder.folder_id,
                                                     blind_trial_num=blind_trial_num)
                            blind_trial.add_to_db()

                        trial_score = SRTrialScore.query.filter_by(trial_id=blind_trial.trial_id,
                                                                   reviewer_id=reviewer.reviewer_id).first()

                        if trial_score is None:
                            SRTrialScore(trial_id=blind_trial.trial_id,
                                         reviewer_id=blind_trial.reviewer_id,
                                         reach_score=int(scored_row['Score'])).add_to_db()
                        elif trial_score.reach_score == int(scored_row['Score']):
                            continue
                        else:
                            trial_score.reach_score = int(scored_row['Score'])
                            # Do I need to create an update method? Look for integrity errors on return
                            trial_score.add_to_db()

                else:
                    print(f"Not Scored: {str(scored_blind_folder_path)}")

    def update_from_dirs(self):
        super()._update_sessions()
        super()._update_folders()
        super()._update_trials()
        self._update_trial_scores()

    def merge_from_work(self, back_up_dir):

        # The goal of this method is to selectively merge sessions, folders, trials, blind_folders, and blind_trials
        # for this experiment only from the back_up_csv files
        back_up_path = Path(back_up_dir)

        remote_exp_table = pd.read_csv(back_up_path.joinpath('experiments.csv'))
        remote_sessions_table = pd.read_csv(back_up_path.joinpath('sessions.csv'))
        remote_folders_table = pd.read_csv(back_up_path.joinpath('folders.csv'))
        remote_trials_table = pd.read_csv(back_up_path.join('trials.csv'))
        remote_blind_folders_table = pd.read_csv(back_up_path.join('blind_folders.csv'))
        remote_blind_trials_table = pd.read_csv(back_up_path.join('blind_trials.csv'))

        remote_exp = remote_exp_table.query(f'experiment_name == "{self.experiment_name}"')

        if remote_exp.experiment_id.item() != str(self.experiment_id):
            print('wtf')
            breakpoint()

        # sessions
        remote_sessions_this_exp = remote_sessions_table.query(f'experiment_id == "{self.experiment_id}"')
        for index, remote_session in remote_sessions_this_exp.iterrows():
            session = Session.query.get(remote_session.session_id)
            if session is None:
                Session(session_id=remote_session.session_id,
                        mouse_id=remote_session.mouse_id,
                        experiment_id=remote_session.experiment_id,
                        session_date=Date.as_date(remote_session.session_date.replace('-', '')),
                        session_dir=remote_session.session_dir,
                        session_num=remote_session.session_num,
                        poly_discrim=remote_session.poly_discrim).add_to_db()
                session = Session.query.get(remote_session.session_id)

            # folders
            remote_folders_this_session = remote_folders_table.query(f'session_id == "{session.session_id}"')
            if len(session.folders) != len(remote_folders_this_session):
                for idx, remote_folder in remote_folders_this_session.iterrows():
                    folder = Folder.query.get(remote_folder.folder_id)
                    if folder is None:
                        Folder(folder_id=remote_folder.folder_id,
                               session_id=remote_folder.session_id,
                               folder_dir=remote_folder.folder_dir,
                               original_video=remote_folder.original_video,
                               trial_frame_number_file=remote_folder.trial_frame_number_file).add_to_db()
                        folder = Folder.query.get(remote_folder.folder_id)

                        # blind folders
                        remote_bf_this_folder = remote_blind_folders_table.query(f'folder_id == "{folder.folder_id}"')
                        if len(folder.score_folders) != len(remote_bf_this_folder):
                            for idx2, remote_bf in remote_bf_this_folder.iterrows():
                                blind_folder = BlindFolder.query.get(remote_bf.blind_folder_id)
                                if blind_folder is None:
                                    BlindFolder(blind_folder_id=remote_bf.blind_folder_id,
                                                folder_id=remote_bf.folder_id,
                                                reviewer_id=remote_bf.reviewer_id,
                                                blind_name=remote_bf.blind_name).add_to_db()

            # trials
            remote_trials_this_session = remote_trials_table.query(f'session_id == "{session.session_id}')
            if len(session.trials) != len(remote_trials_this_session):
                for idx, remote_trial in remote_trials_this_session:
                    trial = Trial.query.get(remote_trial.trial_id)
                    if trial is None:
                        Trial(trial_id=remote_trial.trial_id,
                              experiment_id=remote_trial.experiment_id,
                              session_id=remote_trial.session_id,
                              folder_id=remote_trial.folder_id,
                              trial_dir=remote_trial.trial_dir,
                              trial_date=Date.as_date(remote_trial.trial_date.replate('-', '')),
                              trial_num=remote_trial.trial_num).add_to_db()
                        trial = Trial.query.get(remote_trial.trial_id)

                    # blind trials
                    remote_blind_trials = remote_blind_trials_table.query(f'trial_id == "{trial.trial_id}"')
                    for idx2, remote_bt in remote_blind_trials.iterrows():
                        blind_trial = BlindTrial.query.get(remote_bt.blind_trial_id)
                        if blind_trial is None:
                            BlindTrial(blind_trial_id=remote_bt.blind_trial_id,
                                       blind_folder_id=remote_bt.blind_folder_id,
                                       reviewer_id=remote_bt.reivewer_id,
                                       trial_id=remote_bt.trial_id,
                                       folder_id=remote_bt.folder_id,
                                       blind_trial_num=remote_bt.blind_trial_num).add_to_db()


class DlxChatSapSkilledReaching(DlxSkilledReaching):
    __mapper_args__ = {'polymorphic_identity': 'dlxCKO-chatSap-skilled-reaching'}

    experiment_phase = db.Column(db.String, nullable=True)

    def _update_sessions(self):
        if not Path(self.experiment_dir).exists():
            print(f'Experiment directory does not exist: {self.experiment_dir}')

        # noinspection PyTypeChecker
        # doesn't check self.participants is iterable
        for participant in self.participants:

            phases_search_dir = Path(participant.participant_dir)
            all_phases = self.experiment_phase.split('|')
            for phase in all_phases:
                session_search_dir = phases_search_dir.joinpath(phase)
                all_sessions_this_phase = list(session_search_dir.glob(self.session_re))

                for session in all_sessions_this_phase:
                    session_name = session.name
                    _, yyyymmdd, session_num = session_name.split('_')
                    chat_session = ChatSapSession.query.filter_by(session_dir=str(session)).first()
                    if chat_session is None:
                        ChatSapSession(experiment_phase=phase, mouse_id=participant.mouse_id,
                                       experiment_id=self.experiment_id, session_date=Date.as_date(yyyymmdd),
                                       session_dir=str(session), session_num=int(session_num.strip('T'))).add_to_db()

    def _update_trial_scores(self):
        for folder in self.folders:
            # noinspection PyTypeChecker
            # doesn't check folder.score_folders is iterable
            for blind_folder in folder.score_folders:
                reviewer = Reviewer.query.get(blind_folder.reviewer_id)

                if all([item is not None for item in
                        [SRTrialScore.query.filter_by(
                            trial_id=blind_trial.trial_id,
                            reviewer_id=reviewer.reviewer_id).first()
                         for blind_trial in blind_folder.blind_trials]]):
                    continue

                else:

                    scored_blind_folder_path = Path(reviewer.scored_dir).joinpath(
                        f"{blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")

                    if scored_blind_folder_path.exists():
                        try:
                            all_blind_folder_scores = pd.read_csv(
                                scored_blind_folder_path,
                                usecols=['Trial', 'Score', 'Movement', 'Grooming'],
                                delimiter=',',
                                dtype={'Trial': float, 'Score': float, 'Movement': str, 'Grooming': str}
                            )
                        except ValueError:
                            try:
                                all_blind_folder_scores = pd.read_csv(
                                    scored_blind_folder_path,
                                    usecols=['Trial', 'Score', 'Movement', 'Grooming '],
                                    delimiter=',',
                                    dtype={'Trial': float, 'Score': float, 'Movement': str, 'Grooming ': str}
                                )
                                all_blind_folder_scores['Grooming'] = all_blind_folder_scores['Grooming ']
                            except ValueError:
                                try:
                                    all_blind_folder_scores = pd.read_csv(
                                        scored_blind_folder_path,
                                        usecols=['Trial ', 'Score', 'Movement', 'Grooming'],
                                        delimiter=',',
                                        dtype={'Trial ': float, 'Score': float, 'Movement': str, 'Grooming': str}
                                    )
                                    all_blind_folder_scores['Trial'] = all_blind_folder_scores['Trial ']
                                except ValueError:
                                    print(f"For god's sake, reformat file {scored_blind_folder_path}")
                        except (ParserError, ValueError):
                            print(f"Reformat file {scored_blind_folder_path}")
                            shutil.move(str(scored_blind_folder_path), str(Path(reviewer.scored_dir).parent))
                            continue

                        for index, scored_row in all_blind_folder_scores.iterrows():

                            if isnan(scored_row['Trial']) or isnan(scored_row['Score']):
                                continue

                            blind_trial = BlindTrial.query.filter_by(blind_folder_id=blind_folder.blind_folder_id,
                                                                     reviewer_id=reviewer.reviewer_id,
                                                                     blind_trial_num=int(scored_row['Trial'])).first()

                            if blind_trial is None:
                                blind_trial_num = int(scored_row['Trial'])
                                trial = Trial.query.filter_by(folder_id=folder.folder_id,
                                                              trial_num=blind_trial_num).first()
                                if trial is None:
                                    print('Trial is none?')
                                    continue
                                blind_trial = BlindTrial(blind_folder_id=blind_folder.blind_folder_id,
                                                         reviewer_id=reviewer.reviewer_id,
                                                         trial_id=trial.trial_id,
                                                         folder_id=folder.folder_id,
                                                         blind_trial_num=blind_trial_num)
                                blind_trial.add_to_db()

                            if scored_row['Movement'] == '1':
                                movt = True
                            elif scored_row['Movement'] == '0':
                                movt = False
                            else:
                                movt = None

                            if scored_row['Grooming'] == '1':
                                groom = True
                            elif scored_row['Grooming'] == '0':
                                groom = False
                            else:
                                groom = None

                            trial_score = SRTrialScore.query.filter_by(trial_id=blind_trial.trial_id).filter_by(
                                reviewer_id=reviewer.reviewer_id).first()

                            if trial_score is None:
                                if groom is None:
                                    print('I guess we have to figure this out now')
                                SRTrialScore(trial_id=blind_trial.trial_id,
                                             reviewer_id=blind_trial.reviewer_id,
                                             reach_score=int(scored_row['Score']),
                                             abnormal_movt_score=movt,
                                             grooming_score=groom).add_to_db()
                            elif all([trial_score.reach_score == int(scored_row['Score']),
                                      trial_score.abnormal_movt_score == movt,
                                      trial_score.grooming_score == groom]):
                                continue
                            else:
                                trial_score.reach_score = int(scored_row['Score'])
                                trial_score.abnormal_movt_score = movt
                                trial_score.grooming_score = groom
                                trial_score.add_to_db()

                    else:
                        print(f"Not Scored: {str(scored_blind_folder_path)}")

    def update_from_dirs(self):
        self._update_sessions()
        super()._update_folders()
        super()._update_trials()
        self._update_trial_scores()

    def merge_from_work(self, back_up_dir):

        # The goal of this method is to selectively merge sessions, folders, trials, blind_folders, and blind_trials
        # for this experiment only from the back_up_csv files
        back_up_path = Path(back_up_dir)

        remote_exp_table = pd.read_csv(back_up_path.joinpath('experiments.csv'))
        remote_mice_path = back_up_path.joinpath('mice.csv')
        remote_participant_details_path = back_up_path.joinpath('participant_details.csv')
        remote_sessions_table = pd.read_csv(back_up_path.joinpath('sessions.csv'))
        remote_folders_table = pd.read_csv(back_up_path.joinpath('folders.csv'))
        remote_trials_table = pd.read_csv(back_up_path.joinpath('trials.csv'))
        remote_blind_folders_table = pd.read_csv(back_up_path.joinpath('blind_folders.csv'))
        remote_blind_trials_table = pd.read_csv(back_up_path.joinpath('blind_trials.csv'))

        Mouse.reinstate(remote_mice_path)
        ParticipantDetail.reinstate(remote_participant_details_path)

        remote_exp = remote_exp_table.query(f'experiment_name == "{self.experiment_name}"')

        if remote_exp.experiment_id.item() != str(self.experiment_id):
            print('wtf')
            breakpoint()

        # sessions
        remote_sessions_this_exp = remote_sessions_table.query(f'experiment_id == "{self.experiment_id}"')
        for index, remote_session in remote_sessions_this_exp.iterrows():
            session = Session.query.get(remote_session.session_id)
            if session is None:
                ChatSapSession(session_id=remote_session.session_id,
                               mouse_id=remote_session.mouse_id,
                               experiment_id=remote_session.experiment_id,
                               session_date=Date.as_date(remote_session.session_date.replace('-', '')),
                               session_dir=remote_session.session_dir,
                               session_num=remote_session.session_num,
                               experiment_phase=remote_session.experiment_phase,
                               poly_discrim=remote_session.poly_discrim).add_to_db()
                session = Session.query.get(remote_session.session_id)

            # folders
            remote_folders_this_session = remote_folders_table.query(f'session_id == "{session.session_id}"')
            if len(session.folders) != len(remote_folders_this_session):
                for idx, remote_folder in remote_folders_this_session.iterrows():
                    folder_from_id = Folder.query.get(remote_folder.folder_id)
                    folder_from_dir = Folder.query.filter_by(folder_dir=remote_folder.folder_dir).first()
                    if folder_from_id is None and folder_from_dir is None:
                        Folder(folder_id=remote_folder.folder_id,
                               session_id=remote_folder.session_id,
                               folder_dir=remote_folder.folder_dir,
                               original_video=remote_folder.original_video,
                               trial_frame_number_file=remote_folder.trial_frame_number_file).add_to_db()
                    elif folder_from_id is None and folder_from_dir is not None:
                        folder_from_dir.folder_id = remote_folder.folder_id
                        folder_from_dir.update()
                    elif folder_from_id is not None and folder_from_dir is None:
                        folder_from_id.folder_dir = remote_folder.folder_dir
                        folder_from_id.update()
                    elif folder_from_id is not None and folder_from_dir is not None:
                        if folder_from_id != folder_from_dir:
                            print('what')

                    folder = Folder.query.get(remote_folder.folder_id)

                    # blind folders
                    remote_bf_this_folder = remote_blind_folders_table.query(f'folder_id == "{folder.folder_id}"')
                    if len(folder.score_folders) != len(remote_bf_this_folder):
                        for idx2, remote_bf in remote_bf_this_folder.iterrows():
                            blind_folder = BlindFolder.query.get(remote_bf.blind_folder_id)
                            if blind_folder is None:
                                BlindFolder(blind_folder_id=remote_bf.blind_folder_id,
                                            folder_id=remote_bf.folder_id,
                                            reviewer_id=remote_bf.reviewer_id,
                                            blind_name=remote_bf.blind_name).add_to_db()

                    # trials
                    remote_trials_this_folder = remote_trials_table.query(f'folder_id == "{folder.folder_id}"')
                    if len(folder.trials) != len(remote_trials_this_folder):
                        for idx2, remote_trial in remote_trials_this_folder.iterrows():
                            trial_from_id = Trial.query.get(remote_trial.trial_id)
                            trial_from_dir = Trial.query.filter_by(trial_dir=remote_trial.trial_dir).first()

                            if trial_from_id is None and trial_from_dir is None:
                                Trial(trial_id=remote_trial.trial_id,
                                      experiment_id=remote_trial.experiment_id,
                                      session_id=remote_trial.session_id,
                                      folder_id=remote_trial.folder_id,
                                      trial_dir=remote_trial.trial_dir,
                                      trial_date=Date.as_date(remote_trial.trial_date.replace('-', '')),
                                      trial_num=remote_trial.trial_num).add_to_db()
                            elif trial_from_id is None and trial_from_dir is not None:
                                trial_from_dir.trial_id = remote_trial.trial_id
                                trial_from_dir.update()
                            elif trial_from_id is not None and trial_from_dir is None:
                                trial_from_id.trial_dir = remote_trial.trial_dir
                                trial_from_id.update()
                            elif trial_from_id is not None and trial_from_dir is not None:
                                if trial_from_id == trial_from_dir:
                                    continue
                                print('what')

                            trial = Trial.query.get(remote_trial.trial_id)

                            # blind trials
                            remote_blind_trials = remote_blind_trials_table.query(f'trial_id == "{trial.trial_id}"')
                            for idx3, remote_bt in remote_blind_trials.iterrows():
                                blind_trial = BlindTrial.query.get(remote_bt.blind_trial_id)
                                if blind_trial is None:
                                    BlindTrial(blind_trial_id=remote_bt.blind_trial_id,
                                               blind_folder_id=remote_bt.blind_folder_id,
                                               reviewer_id=remote_bt.reviewer_id,
                                               trial_id=remote_bt.trial_id,
                                               folder_id=remote_bt.folder_id,
                                               blind_trial_num=remote_bt.blind_trial_num).add_to_db()


class DlxGrooming(Experiment):
    __mapper_args__ = {'polymorphic_identity': 'dlxCKO-grooming'}

    grooming_trials = relationship(
        "GroomingTrial",
        secondary="join(Session, GroomingTrial, Session.session_id == GroomingTrial.session_id)",
        primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, "
                    "Session.session_id == GroomingTrial.session_id)",
        secondaryjoin="Session.session_id == GroomingTrial.session_id")

    def _update_chains(self, bout: GroomingBout, all_bout_chains):
        all_bout_chains = all_bout_chains.reset_index(drop=True)
        for idx, chain_row in all_bout_chains.iterrows():
            duration = (int(chain_row['end frame']) - int(chain_row['start frame'])) / 100
            complete = False
            if '2' not in chain_row['chain choreography'] and '3' not in chain_row['chain choreography']:
                continue
            elif '4' in chain_row['chain choreography']:
                complete = True

            chain_chor = list(map(int, chain_row['chain choreography'].split('-')))

            num_transitions = len(chain_chor) - 1
            skips = 0
            reverse = 0
            atypical_end = 0

            for seq_num, phase in enumerate(chain_chor):
                if seq_num == num_transitions:
                    if phase != 4:
                        atypical_end += 1
                else:
                    next_phase = chain_chor[seq_num + 1]
                    if phase + 1 == next_phase:
                        continue
                    elif phase - 1 == next_phase:
                        reverse += 1
                    else:
                        skips += 1
            chain = GroomingChain.query.filter_by(grooming_trial_id=bout.grooming_trial_id,
                                                  start_frame=chain_row['start frame']).first()

            if chain is None:
                GroomingChain(grooming_bout_id=bout.grooming_bout_id,
                              grooming_trial_id=bout.grooming_trial_id,
                              chain_string=chain_row['chain choreography'],
                              start_frame=chain_row['start frame'],
                              end_frame=chain_row['end frame'],
                              duration=duration,
                              complete=complete,
                              grooming_phase_1=chain_chor.count(1),
                              grooming_phase_2=chain_chor.count(2),
                              grooming_phase_3=chain_chor.count(3),
                              grooming_phase_4=chain_chor.count(4),
                              num_transitions=len(chain_chor),
                              num_atypical_transitions=skips + reverse + atypical_end,
                              num_skips=skips,
                              num_reverse=reverse,
                              num_atypical_end=atypical_end
                              ).add_to_db()

    def _update_bouts(self, grooming_trial, all_trial_rows, all_trial_chains, chain_idx):
        all_trial_rows = all_trial_rows.reset_index(drop=True)
        all_trial_chains = all_trial_chains.reset_index(drop=True)

        new_bout = None
        continued_flag = False
        for idx, trial_row in all_trial_rows.iterrows():

            if trial_row['Description'].strip() in ['video start', 'video end']:
                continue
            elif trial_row['Description'].strip() == 'bout start' and new_bout is None:
                new_bout = GroomingBout(grooming_trial_id=grooming_trial.grooming_trial_id,
                                        bout_string=trial_row['Sequence'],
                                        start_frame=trial_row['Frame Number'],
                                        bout_length=0,
                                        num_chains=int(trial_row['Chains']),
                                        num_complete_chains=int(trial_row['Complete Chains']))
            elif trial_row['Description'].strip() == 'bout continue' and new_bout is not None:
                [idx_video_end] = all_trial_rows['Description'].loc[
                    lambda x: x.str.strip() == 'video end'].index.to_list()
                video_end = all_trial_rows.iloc[idx_video_end]
                new_bout.bout_length += video_end['Frame Number'] - new_bout.start_frame
                new_bout.bout_string = '-'.join([new_bout.bout_string, trial_row['Sequence']])
                new_bout.num_chains += int(trial_row['Chains'])
                new_bout.num_complete_chains += int(trial_row['Complete Chains'])
                continued_flag = True
            elif trial_row['Description'].strip() == 'bout end' and new_bout is not None:
                new_bout.end_frame = trial_row['Frame Number']
                if continued_flag:
                    new_bout.bout_length = (new_bout.bout_length + new_bout.end_frame) / 100
                else:
                    new_bout.bout_length = (new_bout.end_frame - new_bout.start_frame) / 100

                bout = GroomingBout.query.filter_by(grooming_trial_id=grooming_trial.grooming_trial_id,
                                                    bout_string=new_bout.bout_string).first()
                if bout is None:
                    new_bout.add_to_db()
                elif not new_bout.is_same(bout):
                    bout.bout_string = new_bout.bout_string
                    bout.start_frame = new_bout.start_frame
                    bout.end_frame = new_bout.end_frame
                    bout.bout_length = new_bout.bout_length
                    bout.chains_perMin = new_bout.num_chains
                    bout.num_complete_chains = new_bout.num_complete_chains
                    bout.add_to_db()

                bout = GroomingBout.query.filter_by(grooming_trial_id=new_bout.grooming_trial_id,
                                                    bout_string=new_bout.bout_string).first()
                new_bout = None
                continued_flag = False

                if bout.chains_perMin > 0:
                    self._update_chains(bout,
                                        all_trial_chains.iloc[int(chain_idx):int(chain_idx) + int(bout.chains_perMin)])
                    chain_idx += bout.chains_perMin

    def _update_grooming_trials(self):

        for session in self.sessions:

            session_dir = Path(session.session_dir)
            score_sheet_paths = list(session_dir.glob('*_*_*.xlsx'))

            if len(score_sheet_paths) == 0:
                continue

            score_sheet_paths.sort()
            bouts_df = pd.DataFrame()
            chains_df = pd.DataFrame()
            chain_idx = 0
            for score_sheet_path in score_sheet_paths:
                xls_score_sheet = pd.ExcelFile(score_sheet_path, engine='openpyxl')
                bouts_df = pd.concat([bouts_df, pd.read_excel(xls_score_sheet, 'bouts').fillna(0)])
                chains_df = pd.concat([chains_df, pd.read_excel(xls_score_sheet, 'chains').fillna(0)])

            bouts_df = bouts_df.reset_index(drop=True)
            chains_df = chains_df.reset_index(drop=True)

            if 'Chains' not in bouts_df.columns.to_list() or 'Complete Chains' not in bouts_df.columns.to_list():
                print(f'reformat file: {session.session_dir}')
                continue

            idx_all_trial_start = bouts_df['Description'].loc[lambda x: x == 'trial start'].index.to_list()
            idx_all_trial_end = bouts_df['Description'].loc[lambda x: x == 'trial end'].index.to_list()
            all_trial_idx = list(zip(idx_all_trial_start, idx_all_trial_end))

            if len(all_trial_idx) == 0:
                num_sheets_first_trial = round(len(score_sheet_paths) / 2)

                bouts_1_df = pd.DataFrame()
                chains_1_df = pd.DataFrame()
                bouts_2_df = pd.DataFrame()
                chains_2_df = pd.DataFrame()
                for score_sheet_path in score_sheet_paths[0:num_sheets_first_trial]:
                    xls_score_sheet = pd.ExcelFile(score_sheet_path, engine='openpyxl')
                    bouts_1_df = pd.concat([bouts_1_df, pd.read_excel(xls_score_sheet, 'bouts').fillna(0)])
                    chains_1_df = pd.concat([chains_1_df, pd.read_excel(xls_score_sheet, 'chains').fillna(0)])

                for score_sheet_path in score_sheet_paths[num_sheets_first_trial:]:
                    xls_score_sheet = pd.ExcelFile(score_sheet_path, engine='openpyxl')
                    bouts_2_df = pd.concat([bouts_2_df, pd.read_excel(xls_score_sheet, 'bouts').fillna(0)])
                    chains_2_df = pd.concat([chains_2_df, pd.read_excel(xls_score_sheet, 'chains').fillna(0)])

                bouts_1_df = bouts_1_df.reset_index(drop=True)
                chains_1_df = chains_1_df.reset_index(drop=True)
                bouts_2_df = bouts_2_df.reset_index(drop=True)
                chains_2_df = chains_2_df.reset_index(drop=True)

                for trial_num, (bouts_df, chains_df) in enumerate(
                        [(bouts_1_df, chains_1_df), (bouts_2_df, chains_2_df)]):
                    if 'Chains' not in bouts_df.columns.to_list() or 'Complete Chains' not in bouts_df.columns.to_list():
                        print(f'reformat file: {session.session_dir}')
                        continue

                    try:
                        idx_all_bout_start = bouts_df['Description'].loc[lambda x: x == 'bout start'].index.to_list()
                        all_bout_start_rows = bouts_df.iloc[idx_all_bout_start]
                    except IndexError:
                        breakpoint()

                    idx_all_bout_end = bouts_df['Description'].loc[lambda x: x == 'bout end'].index.to_list()
                    all_bout_end_rows = bouts_df.iloc[idx_all_bout_end]

                    total_frames_grooming = all_bout_end_rows['Frame Number'].sum() - all_bout_start_rows[
                        'Frame Number'].sum()
                    num_bouts = len(all_bout_start_rows)

                    num_chains = all_bout_start_rows['Chains'].sum()
                    num_complete_chains = all_bout_start_rows['Complete Chains'].sum()

                    grooming_trial = GroomingTrial.query.filter_by(session_id=session.session_id,
                                                                   trial_num=trial_num + 1).first()

                    if grooming_trial is None:
                        GroomingTrial(session_id=session.session_id,
                                      scored_session_dir=session.session_dir,
                                      trial_num=trial_num + 1,
                                      total_time_grooming=total_frames_grooming.item() / 100,
                                      num_bouts=num_bouts,
                                      num_chains=num_chains.item(),
                                      num_complete_chains=num_complete_chains.item()).add_to_db()

                        grooming_trial = GroomingTrial.query.filter_by(session_id=session.session_id,
                                                                       trial_num=trial_num + 1).first()

                    self._update_bouts(grooming_trial, bouts_df, chains_df.iloc[int(chain_idx):int(num_chains)],
                                       chain_idx)
                    chain_idx += num_chains.item()

            for trial_num, [trial_start_idx, trial_end_idx] in enumerate(all_trial_idx):
                chain_idx = 0
                trial_start_row = bouts_df.iloc[trial_start_idx]
                trial_end_row = bouts_df.iloc[trial_end_idx]
                all_trial_rows = bouts_df.iloc[trial_start_idx + 1:trial_end_idx]

                idx_all_bout_start = all_trial_rows['Description'].loc[
                    lambda x: x.str.strip() == 'bout start'].index.to_list()
                all_bout_start_rows = bouts_df.iloc[idx_all_bout_start]

                idx_all_bout_end = all_trial_rows['Description'].loc[
                    lambda x: x.str.strip() == 'bout end'].index.to_list()
                all_bout_end_rows = bouts_df.iloc[idx_all_bout_end]

                if len(all_bout_start_rows) != len(all_bout_end_rows):
                    breakpoint()

                try:
                    idx_video_end = all_trial_rows['Description'].loc[
                        lambda x: x.str.strip() == 'video end'].index.item()
                    row_video_end = bouts_df.iloc[idx_video_end]
                    trial_length = (row_video_end['Frame Number'] - trial_start_row['Frame Number'] + trial_end_row[
                        'Frame Number']) / 100
                except ValueError:
                    trial_length = (trial_end_row['Frame Number'] - trial_start_row['Frame Number']) / 100

                total_frames_grooming = (all_bout_end_rows['Frame Number'].sum() -
                                         all_bout_start_rows['Frame Number'].sum())
                idx_all_bout_continue = all_trial_rows['Description'].loc[
                    lambda x: x.str.strip() == 'bout continue'].index.to_list()
                if len(idx_all_bout_continue) > 0:
                    for continue_idx in idx_all_bout_continue:
                        rows_before_continue = bouts_df.iloc[trial_start_idx + 1:continue_idx]
                        idx_video_end = rows_before_continue['Description'].loc[
                            lambda x: x.str.strip() == 'video end'].index.item()
                        row_video_end = bouts_df.iloc[idx_video_end]
                        total_frames_grooming += row_video_end['Frame Number']

                try:
                    rows_trial_start_first_bout = bouts_df.iloc[trial_start_idx + 1:idx_all_bout_start[0]]
                    idx_video_end = rows_trial_start_first_bout['Description'].loc[
                        lambda x: x.str.strip() == 'video end'].index.item()
                    row_video_end = bouts_df.iloc[idx_video_end]
                    latency_to_onset = (row_video_end['Frame Number'] - trial_start_row['Frame Number'] +
                                        bouts_df.loc[idx_all_bout_start[0]]['Frame Number']) / 100
                except ValueError:
                    latency_to_onset = (bouts_df.loc[idx_all_bout_start[0]]['Frame Number'] -
                                        trial_start_row['Frame Number']) / 100

                num_bouts = len(all_bout_start_rows)

                num_chains = all_bout_start_rows['Chains'].sum()
                num_complete_chains = all_bout_start_rows['Complete Chains'].sum()

                grooming_trial = GroomingTrial.query.filter_by(session_id=session.session_id,
                                                               trial_num=trial_num + 1).first()
                if grooming_trial is None:
                    GroomingTrial(session_id=session.session_id,
                                  scored_session_dir=session.session_dir,
                                  trial_num=trial_num + 1,
                                  trial_length=trial_length,
                                  total_time_grooming=total_frames_grooming.item() / 100,
                                  latency_to_onset=latency_to_onset,
                                  num_bouts=num_bouts,
                                  num_chains=num_chains.item(),
                                  num_complete_chains=num_complete_chains.item()).add_to_db()

                    grooming_trial = GroomingTrial.query.filter_by(session_id=session.session_id,
                                                                   trial_num=trial_num + 1).first()

                self._update_bouts(grooming_trial, all_trial_rows, chains_df.iloc[int(chain_idx):int(num_chains)],
                                   chain_idx)
                chain_idx += num_chains

    def update_from_dirs(self):
        self._update_grooming_trials()


class DlxPastaHandling(Experiment):
    __mapper_args__ = {'polymorphic_identity': 'dlxCKO-pasta-handling'}

    scored_pasta_handling = relationship("PastaHandlingScores",
                                         secondary="join(Session, PastaHandlingScores, "
                                                   "Session.session_id == PastaHandlingScores.session_id)",
                                         primaryjoin="and_(Session.experiment_id == Experiment.experiment_id, "
                                                     "Session.session_id == PastaHandlingScores.session_id)",
                                         secondaryjoin="Session.session_id == PastaHandlingScores.session_id")

    def _update_pasta_handling_scores(self):
        # noinspection PyTypeChecker
        for session in self.sessions:
            all_scored_trials = list(Path(session.session_dir).glob("*.xlsx"))

            if len(all_scored_trials) == 0:
                continue

            for scored_trial in all_scored_trials:

                trial_num = str(scored_trial.stem).split('_')[-1]
                trial_num = int(trial_num.strip('T'))

                score_sheet = pd.read_excel(scored_trial, engine='openpyxl', index_col=0).transpose()

                boolean_values = {"Left Forepaw Failure to Contact": False,
                                  "Right Forepaw Failure to Contact": False,
                                  "Guide and Grasp Switch": False,
                                  "Drop Count": False,
                                  "Mouth Pulling": False,
                                  "Paws Together, Pasta Long": False,
                                  "Paws Apart, Pasta Short": False,
                                  "Abnormal Posture": False,
                                  "Iron Grip": False,
                                  "Guide Around Grasp": False,
                                  "Angling with Head Tilt": False}

                for key in boolean_values.keys():
                    if score_sheet[key].any() > 0:
                        boolean_values[key] = True

                PastaHandlingScores(session_id=session.session_id,
                                    scored_session_dir=str(scored_trial),
                                    trial_num=trial_num,
                                    time_to_eat=score_sheet["Eating Time"]['value'],
                                    grasp_paw_start=score_sheet["Grasp Paw (at start)"]['value'],
                                    guide_paw_start=score_sheet["Guide/Support Paw (at start)"]['value'],
                                    left_forepaw_adjustments=score_sheet["Left Forepaw Adjustments"]['value'],
                                    right_forepaw_adjustments=score_sheet["Right Forepaw Adjustments"]['value'],
                                    left_forepaw_failure_to_contact=score_sheet[
                                        "Left Forepaw Failure to Contact"]['value'],
                                    right_forepaw_failure_to_contact=score_sheet[
                                        "Right Forepaw Failure to Contact"]['value'],
                                    guide_grasp_switch=score_sheet["Guide and Grasp Switch"]['value'],
                                    drops=score_sheet["Drop Count"]['value'],
                                    mouth_pulling=score_sheet["Mouth Pulling"]['value'],
                                    pasta_long_paws_together=score_sheet["Paws Together, Pasta Long"]['value'],
                                    pasta_short_paws_apart=score_sheet["Paws Apart, Pasta Short"]['value'],
                                    abnormal_posture=score_sheet["Abnormal Posture"]['value'],
                                    iron_grip=score_sheet["Iron Grip"]['value'],
                                    guide_around_grasp=score_sheet["Guide Around Grasp"]['value'],
                                    angling_with_head_tilt=score_sheet["Angling with Head Tilt"]['value'],
                                    left_forepaw_failure_to_contact_bool=boolean_values[
                                        "Left Forepaw Failure to Contact"],
                                    right_forepaw_failure_to_contact_bool=boolean_values[
                                        "Right Forepaw Failure to Contact"],
                                    guide_grasp_switch_bool=boolean_values["Guide and Grasp Switch"],
                                    drops_bool=boolean_values["Drop Count"],
                                    mouth_pulling_bool=boolean_values["Mouth Pulling"],
                                    pasta_long_paws_together_bool=boolean_values["Paws Together, Pasta Long"],
                                    pasta_short_paws_apart_bool=boolean_values["Paws Apart, Pasta Short"],
                                    abnormal_posture_bool=boolean_values["Abnormal Posture"],
                                    iron_grip_bool=boolean_values["Iron Grip"],
                                    guide_around_grasp_bool=boolean_values["Guide Around Grasp"],
                                    angling_with_head_tilt_bool=boolean_values["Angling with Head Tilt"]
                                    ).add_to_db()

    def update_from_dirs(self):
        self._update_sessions()
        self._update_pasta_handling_scores()
