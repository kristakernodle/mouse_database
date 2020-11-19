import json
from pathlib import Path

import pandas as pd

from database_pkg import db, Mouse, Experiment, ParticipantDetail, Reviewer, Session, Folder, Trial, BlindFolder, \
    BlindTrial
from database_pkg.utilities import parse_date, Date


def reinstate_mouse(full_path):
    mouse_data_frame = pd.read_csv(full_path,
                                   usecols=['mouse_id', 'eartag', 'birthdate', 'genotype', 'sex'],
                                   delimiter=',',
                                   dtype={'mouse_id': str, 'eartag': str, 'birthdate': str, 'genotype': str,
                                          'sex': str},
                                   nrows=23)
    mouse_data_frame.genotype = mouse_data_frame.genotype.apply(lambda x: x == 'TRUE')
    mouse_data_frame.birthdate = mouse_data_frame.birthdate.apply(lambda x: parse_date(x))
    for index, mouse_row in mouse_data_frame.iterrows():
        if Mouse.query.get(mouse_row["mouse_id"]) is None:
            db.session.add(
                Mouse(mouse_id=mouse_row["mouse_id"], eartag=int(mouse_row["eartag"]),
                      birthdate=mouse_row["birthdate"], genotype=mouse_row["genotype"],
                      sex=mouse_row["sex"])
            )
            db.session.commit()


def reinstate_experiments(full_path):
    experiments_data_frame = pd.read_csv(full_path, delimiter=',',
                                         dtype={'experiment_id': str, 'experiment_dir': str, 'experiment_name': str,
                                                'session_re': str, 'folder_re': str, 'trial_re': str})
    for index, experiment_row in experiments_data_frame.iterrows():
        if Experiment.query.get(experiment_row["experiment_id"]) is None:
            db.session.add(
                Experiment(experiment_id=experiment_row["experiment_id"],
                           experiment_dir=experiment_row["experiment_dir"],
                           experiment_name=experiment_row["experiment_name"],
                           session_re=experiment_row["session_re"],
                           folder_re=experiment_row["folder_re"],
                           trial_re=experiment_row["trial_re"])
            )
            db.session.commit()


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
        if any([Mouse.query.get(detail_row["mouse_id"]) is None,
                Experiment.query.get(detail_row["experiment_id"]) is None]):
            print('Mouse or experiment does not exist')
        elif ParticipantDetail.query.get(detail_row["detail_id"]) is None:

            if type(detail_row["exp_spec_details"]) is not str:
                exp_spec_details = None
            else:
                exp_spec_details = json.loads(detail_row["exp_spec_details"])
            db.session.add(
                ParticipantDetail(detail_id=detail_row["detail_id"], mouse_id=detail_row["mouse_id"],
                                  experiment_id=detail_row["experiment_id"],
                                  start_date=Date.as_date(detail_row["start_date"]),
                                  end_date=Date.as_date(detail_row["end_date"]),
                                  participant_dir=detail_row["participant_dir"],
                                  exp_spec_details=exp_spec_details)
            )
            db.session.commit()


def reinstate_reviewers(full_path):
    reviewer_data_frame = pd.read_csv(full_path,
                                      usecols=['reviewer_id', 'first_name', 'last_name', 'toscore_dir', 'scored_dir'],
                                      delimiter=',',
                                      dtype={'reviewer_id': str, 'first_name': str,
                                             'last_name': str, 'toscore_dir': str,
                                             'scored_dir': str},
                                      nrows=6)
    for index, reviewer_row in reviewer_data_frame.iterrows():
        if Reviewer.query.get(reviewer_row["reviewer_id"]) is None:
            db.session.add(
                Reviewer(reviewer_id=reviewer_row["reviewer_id"], first_name=reviewer_row["first_name"],
                         last_name=reviewer_row["last_name"], toScore_dir=reviewer_row["toscore_dir"],
                         scored_dir=reviewer_row["scored_dir"])
            )
            db.session.commit()


def reinstate_sessions(full_path):
    sessions_data_frame = pd.read_csv(full_path,
                                      usecols=['session_id', 'mouse_id', 'experiment_id', 'session_dir', 'session_num'],
                                      delimiter=',',
                                      dtype={'session_id': str, 'mouse_id': str, 'experiment_id': str,
                                             'session_dir': str, 'session_num': int}
                                      )
    for index, session_row in sessions_data_frame.iterrows():
        mouse = Mouse.query.get(session_row['mouse_id'])
        experiment = Experiment.query.get(session_row['experiment_id'])
        session = Session.query.get(session_row['session_id'])
        if mouse is not None and experiment is not None and session is None:
            session_date = Date.as_date(str(session_row['session_dir']).split('_')[1])
            db.session.add(
                Session(session_id=session_row['session_id'], mouse_id=session_row['mouse_id'],
                        experiment_id=session_row['experiment_id'], session_date=session_date,
                        session_dir=session_row['session_dir'], session_num=session_row['session_num']
                        )
            )
            db.session.commit()
        else:
            print(session_row)


def reinstate_folders(full_path):
    folders_data_frame = pd.read_csv(full_path,
                                     usecols=['folder_id', 'session_id', 'folder_dir'],
                                     delimiter=',',
                                     dtype={'folder_id': str, 'session_id': str, 'folder_dir': str}
                                     )
    for index, folder_row in folders_data_frame.iterrows():
        session = Session.query.get(folder_row['session_id'])
        folder = Folder.query.get(folder_row['folder_id'])
        if session is not None and folder is None:
            folder_num = folder_row['folder_dir'].split('Reaches')[-1]
            original_video_stem = '_'.join(Path(session.session_dir).name.strip('et').split('_')[:-1])
            original_video = Path(session.session_dir).joinpath(f"{original_video_stem}_{folder_num}.MP4")
            trial_frame_number_file = Path(session.session_dir).joinpath(f"{original_video_stem}_{folder_num}.csv")
            db.session.add(
                Folder(folder_id=folder_row['folder_id'], session_id=folder_row['session_id'],
                       folder_dir=folder_row['folder_dir'],
                       original_video=str(original_video), trial_frame_number_file=str(trial_frame_number_file))
            )
            db.session.commit()


def reinstate_trials(full_path):
    trials_data_frame = pd.read_csv(full_path,
                                    usecols=['trial_id', 'experiment_id', 'folder_id', 'trial_dir', 'trial_date'],
                                    delimiter=',',
                                    dtype={'trial_id': str, 'experiment_id': str, 'folder_id': str, 'trial_dir': str,
                                           'trial_date': str}
                                    )
    for index, trial_row in trials_data_frame.iterrows():
        trial = Trial.query.get(trial_row['trial_id'])
        experiment = Experiment.query.get(trial_row['experiment_id'])
        folder = Folder.query.get(trial_row['folder_id'])
        session = Session.query.get(folder.session_id)
        if trial is None and experiment is not None and session is not None and folder is not None:
            trial_num_temp = str(trial_row['trial_dir']).split('_')[-1]
            trial_num_temp = trial_num_temp.split('R')[-1]
            trial_num = int(trial_num_temp.split('.')[0])
            trial_date = Date.as_date(trial_row['trial_dir'].split('_')[1])
            db.session.add(
                Trial(trial_id=trial_row['trial_id'], experiment_id=trial_row['experiment_id'],
                      session_id=session.session_id, folder_id=trial_row['folder_id'], trial_dir=trial_row['trial_dir'],
                      trial_date=trial_date, trial_num=trial_num)
            )
            db.session.commit()


def reinstate_blind_folders(full_path):
    blind_folders_df = pd.read_csv(full_path,
                                   usecols=['blind_folder_id', 'folder_id', 'reviewer_id', 'blind_name'],
                                   delimiter=',',
                                   dtype={'blind_folder_id': str, 'folder_id': str, 'reviewer_id': str,
                                          'blind_name': str}
                                   )
    for index, blind_folder_row in blind_folders_df.iterrows():
        blind_folder = BlindFolder.query.get(blind_folder_row['blind_folder_id'])

        if blind_folder is not None:
            continue

        blind_folder = BlindFolder.query.filter(BlindFolder.blind_name == blind_folder_row['blind_name']).first()

        if blind_folder is not None:
            continue

        folder = Folder.query.get(blind_folder_row['folder_id'])
        reviewer = Reviewer.query.get(blind_folder_row['reviewer_id'])
        if folder is not None and reviewer is not None:
            db.session.add(
                BlindFolder(blind_folder_id=blind_folder_row['blind_folder_id'],
                        folder_id=blind_folder_row['folder_id'],
                        reviewer_id=blind_folder_row['reviewer_id'], blind_name=blind_folder_row['blind_name']
                            )
            )
            db.session.commit()
        else:
            print(f'Inspect blind_folder_id: {blind_folder_row.blind_folder_id} \n'
                  f'Inspect folder_id: {blind_folder_row.folder_id} \n'
                  f'Inspect reviewer_id: {blind_folder_row.reviewer_id}.')


def reinstate_blind_trials(full_path):
    blind_trials_df = pd.read_csv(full_path,
                                  usecols=['blind_trial_id', 'trial_id', 'folder_id', 'full_path'],
                                  delimiter=',',
                                  dtype={'blind_trial_id': str, 'trial_id': str, 'folder_id': str, 'full_path': str}
                                  )
    for index, blind_trial_row in blind_trials_df.iterrows():
        blind_trial = BlindTrial.query.get(blind_trial_row['blind_trial_id'])

        if blind_trial is not None:
            continue

        trial = Trial.query.get(blind_trial_row['trial_id'])
        folder = Folder.query.get(blind_trial_row['folder_id'])

        reviewer_name_temp = blind_trial_row['full_path'].split('/')[-4]
        try:
            reviewer_first_name, reviewer_last_name = reviewer_name_temp.split('_')
        except ValueError:
            print(reviewer_name_temp)
            continue

        reviewer = Reviewer.query.filter(Reviewer.first_name == reviewer_first_name
                                         and Reviewer.last_name == reviewer_last_name).first()
        try:
            blind_trial_num_temp = blind_trial_row['full_path'].split('/')[-1]
            blind_name, blind_trial_num_temp = blind_trial_num_temp.split('_R')
            blind_trial_num = int(blind_trial_num_temp.split('.')[0])
        except ValueError:
            blind_trial_num_temp = blind_trial_row['full_path'].split('/')[-1]
            blind_name, blind_trial_num_temp = blind_trial_num_temp.split('_')
            blind_trial_num = int(blind_trial_num_temp.split('.')[0])

        blind_folder = BlindFolder.query.filter(BlindFolder.blind_name == blind_name).first()

        if blind_trial is None \
                and trial is not None \
                and folder is not None \
                and reviewer is not None \
                and blind_folder is not None:
            db.session.add(
                BlindTrial(blind_trial_id=blind_trial_row['blind_trial_id'],
                           blind_folder_id=blind_folder.blind_folder_id, reviewer_id=reviewer.reviewer_id,
                           trial_id=trial.trial_id, folder_id=folder.folder_id, blind_trial_num=blind_trial_num)
            )
            db.session.commit()
        else:
            print("Help")
