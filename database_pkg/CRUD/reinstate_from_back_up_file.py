import json

import pandas as pd
from sqlalchemy.exc import IntegrityError

from database_pkg import Mouse, Experiment, ParticipantDetail, Reviewer, Session, Folder, Trial, BlindFolder, \
    BlindTrial, SRTrialScore, db
from database_pkg.utilities import parse_date, Date


def reinstate_mouse(full_path):
    mouse_data_frame = pd.read_csv(full_path,
                                   usecols=['mouse_id', 'eartag', 'birthdate', 'genotype', 'sex'],
                                   delimiter=',',
                                   dtype={'mouse_id': str, 'eartag': str, 'birthdate': str, 'genotype': str,
                                          'sex': str},
                                   nrows=23)
    mouse_data_frame.genotype = mouse_data_frame.genotype.apply(lambda x: x == 'TRUE' or x == 'true')
    mouse_data_frame.birthdate = mouse_data_frame.birthdate.apply(lambda x: parse_date(x))
    for index, mouse_row in mouse_data_frame.iterrows():
        if Mouse.query.get(mouse_row["mouse_id"]) is None:
            Mouse(mouse_id=mouse_row["mouse_id"],
                  eartag=int(mouse_row["eartag"]),
                  birthdate=mouse_row["birthdate"],
                  genotype=mouse_row["genotype"],
                  sex=mouse_row["sex"]).add_to_db()


def reinstate_experiments(full_path):
    experiments_data_frame = pd.read_csv(full_path, delimiter=',',
                                         dtype={'experiment_id': str, 'experiment_dir': str, 'experiment_name': str,
                                                'session_re': str, 'folder_re': str, 'trial_re': str})
    for index, experiment_row in experiments_data_frame.iterrows():
        if Experiment.query.get(experiment_row["experiment_id"]) is None:
            Experiment(experiment_id=experiment_row["experiment_id"],
                       experiment_dir=experiment_row["experiment_dir"],
                       experiment_name=experiment_row["experiment_name"],
                       session_re=experiment_row["session_re"],
                       folder_re=experiment_row["folder_re"],
                       trial_re=experiment_row["trial_re"]).add_to_db()


def reinstate_participant_details(full_path):
    participant_details_df = pd.read_csv(full_path,
                                         usecols=['detail_id', 'mouse_id', 'experiment_id', 'start_date', 'end_date',
                                                  'participant_dir', 'exp_spec_details'],
                                         delimiter=',',
                                         dtype={'detail_id': str, 'mouse_id': str, 'experiment_id': str,
                                                'start_date': str,
                                                'end_date': str, 'participant_dir': str, 'exp_spec_details': str},
                                         nrows=38)
    participant_details_df.start_date = participant_details_df.start_date.apply(lambda x: parse_date(x))
    participant_details_df.end_date = participant_details_df.end_date.apply(lambda x: parse_date(x))

    for index, detail_row in participant_details_df.iterrows():
        if ParticipantDetail.query.get(detail_row["detail_id"]) is None:

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


def reinstate_reviewers(full_path):
    reviewer_data_frame = pd.read_csv(full_path,
                                      usecols=['reviewer_id', 'first_name', 'last_name', 'toScore_dir', 'scored_dir'],
                                      delimiter=',',
                                      dtype={'reviewer_id': str, 'first_name': str,
                                             'last_name': str, 'toScore_dir': str,
                                             'scored_dir': str},
                                      nrows=6)
    for index, reviewer_row in reviewer_data_frame.iterrows():
        if Reviewer.query.get(reviewer_row["reviewer_id"]) is None:
            Reviewer(reviewer_id=reviewer_row["reviewer_id"],
                     first_name=reviewer_row["first_name"],
                     last_name=reviewer_row["last_name"],
                     toScore_dir=reviewer_row["toScore_dir"],
                     scored_dir=reviewer_row["scored_dir"]).add_to_db()


def reinstate_sessions(full_path):
    sessions_data_frame = pd.read_csv(full_path,
                                      usecols=['session_id', 'mouse_id', 'experiment_id', 'session_date', 'session_dir',
                                               'session_num'],
                                      delimiter=',',
                                      dtype={'session_id': str, 'mouse_id': str, 'experiment_id': str,
                                             'session_date': str, 'session_dir': str, 'session_num': int}
                                      )
    sessions_data_frame.session_date = sessions_data_frame.session_date.apply(lambda x: parse_date(x))
    for index, session_row in sessions_data_frame.iterrows():
        if Session.query.get(session_row['session_id']) is None:
            Session(session_id=session_row['session_id'],
                    mouse_id=session_row['mouse_id'],
                    experiment_id=session_row['experiment_id'],
                    session_date=session_row['session_date'],
                    session_dir=session_row['session_dir'],
                    session_num=session_row['session_num']).add_to_db()


def reinstate_folders(full_path):
    folders_data_frame = pd.read_csv(full_path,
                                     usecols=['folder_id', 'session_id', 'folder_dir', 'original_video',
                                              'trial_frame_number_file'],
                                     delimiter=',',
                                     dtype={'folder_id': str, 'session_id': str, 'folder_dir': str,
                                            'original_video': str, 'trial_frame_number_file': str}
                                     )
    for index, folder_row in folders_data_frame.iterrows():
        if Folder.query.get(folder_row['folder_id']) is None:
            Folder(folder_id=folder_row['folder_id'],
                   session_id=folder_row['session_id'],
                   folder_dir=folder_row['folder_dir'],
                   original_video=folder_row['original_video'],
                   trial_frame_number_file=folder_row['trial_frame_number_file']).add_to_db()


def reinstate_trials(full_path):
    trials_data_frame = pd.read_csv(full_path,
                                    usecols=['trial_id', 'experiment_id', 'session_id', 'folder_id', 'trial_dir',
                                             'trial_date', 'trial_num'],
                                    delimiter=',',
                                    dtype={'trial_id': str, 'experiment_id': str, 'session_id': str, 'folder_id': str,
                                           'trial_dir': str, 'trial_date': str, 'trial_num': int}
                                    )
    trials_data_frame.trial_date = trials_data_frame.trial_date.apply(lambda x: parse_date(x))
    for index, trial_row in trials_data_frame.iterrows():
        if Trial.query.get(trial_row['trial_id']) is None:
            Trial(trial_id=trial_row['trial_id'],
                  experiment_id=trial_row['experiment_id'],
                  session_id=trial_row['session_id'],
                  folder_id=trial_row['folder_id'],
                  trial_dir=trial_row['trial_dir'],
                  trial_date=trial_row['trial_date'],
                  trial_num=trial_row['trial_num']).add_to_db()


def reinstate_blind_folders(full_path):
    blind_folders_df = pd.read_csv(full_path,
                                   usecols=['blind_folder_id', 'folder_id', 'reviewer_id', 'blind_name'],
                                   delimiter=',',
                                   dtype={'blind_folder_id': str, 'folder_id': str, 'reviewer_id': str,
                                          'blind_name': str}
                                   )
    for index, blind_folder_row in blind_folders_df.iterrows():
        if BlindFolder.query.get(blind_folder_row['blind_folder_id']) is None:
            BlindFolder(blind_folder_id=blind_folder_row['blind_folder_id'],
                        folder_id=blind_folder_row['folder_id'],
                        reviewer_id=blind_folder_row['reviewer_id'],
                        blind_name=blind_folder_row['blind_name']
                        ).add_to_db()


def reinstate_blind_trials(full_path):
    blind_trials_df = pd.read_csv(full_path,
                                  usecols=['blind_trial_id', 'blind_folder_id', 'reviewer_id', 'trial_id', 'folder_id',
                                           'blind_trial_num'],
                                  delimiter=',',
                                  dtype={'blind_trial_id': str, 'blind_folder_id': str, 'reviewer_id': str,
                                         'trial_id': str, 'folder_id': str, 'blind_trial_num': int}
                                  )
    for index, blind_trial_row in blind_trials_df.iterrows():
        if BlindTrial.query.get(blind_trial_row['blind_trial_id']) is None:
            BlindTrial(blind_trial_id=blind_trial_row['blind_trial_id'],
                       blind_folder_id=blind_trial_row['blind_folder_id'],
                       reviewer_id=blind_trial_row['reviewer_id'],
                       trial_id=blind_trial_row['trial_id'],
                       folder_id=blind_trial_row['folder_id'],
                       blind_trial_num=blind_trial_row['blind_trial_num']).add_to_db()


def reinstate_sr_trial_scores(full_path):
    sr_trial_scores_df = pd.read_csv(full_path,
                                     usecols=['trial_score_id', 'trial_id', 'reviewer_id', 'reach_score',
                                              'abnormal_movt_score', 'grooming_score'],
                                     delimiter=',',
                                     dtype={'trial_score_id': str, 'trial_id': str, 'reviewer_id': str,
                                            'reach_score': int, 'abnormal_movt_score': int, 'grooming_score': int}
                                     )
    for index, sr_trial_score_row in sr_trial_scores_df.iterrows():
        if SRTrialScore.query.get(sr_trial_score_row['trial_score_id']) is None:
            SRTrialScore(trial_score_id=sr_trial_score_row['trial_score_id'],
                         trial_id=sr_trial_score_row['trial_id'],
                         reviewer_id=sr_trial_score_row['reviewer_id'],
                         reach_score=sr_trial_score_row['reach_score'],
                         abnormal_movt_score=sr_trial_score_row['abnormal_movt_score'],
                         grooming_score=sr_trial_score_row['grooming_score']).add_to_db()

## TODO reinstate_grooming_summary


