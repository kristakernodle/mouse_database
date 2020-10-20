import pandas as pd
import json
from pathlib import Path

from database_pkg import db, Date, Mouse, Reviewer, Experiment, ParticipantDetail, Session, Folder, Trial, \
    BlindFolder, BlindTrial
from database_pkg.utilities import parse_date


def reinstate_blind_folders_trials(back_up_dir):
    reviewers_path = Path(back_up_dir).joinpath('reviewers.csv')
    folder_path = Path(back_up_dir).joinpath('folders.csv')
    trial_path = Path(back_up_dir).joinpath('trials.csv')
    blind_folder_path = Path(back_up_dir).joinpath('blind_folders.csv')
    blind_trial_path = Path(back_up_dir).joinpath('blind_trials.csv')

    reviewers_df = pd.read_csv(reviewers_path,
                               usecols=['reviewer_id', 'first_name', 'last_name', 'toscore_dir', 'scored_dir'],
                               delimiter=',',
                               dtype={'reviewer_id': str, 'first_name': str, 'last_name': str, 'toscore_dir': str,
                                      'scored_dir': str})
    folders_df = pd.read_csv(folder_path,
                             usecols=['folder_id', 'folder_dir'],
                             delimiter=',',
                             dtype={'folder_id': str, 'folder_dir': str})
    trials_df = pd.read_csv(trial_path,
                            usecols=['trial_id', 'folder_id', 'trial_dir'],
                            delimiter=',',
                            dtype={'trial_id': str, 'folder_id': str, 'trial_dir': str})
    blind_folders_df = pd.read_csv(blind_folder_path,
                                   usecols=['blind_folder_id', 'folder_id', 'reviewer_id', 'blind_name'],
                                   delimiter=',',
                                   dtype={'blind_folder_id': str, 'folder_id': str, 'reviewer_id': str,
                                          'blind_name': str})
    blind_trials_df = pd.read_csv(blind_trial_path,
                                  usecols=['blind_trial_id', 'trial_id', 'folder_id', 'full_path'],
                                  delimiter=',',
                                  dtype={'blind_trial_id': str, 'trial_id': str, 'folder_id': str, 'full_path': str})

    for index, og_blind_folder in blind_folders_df.iterrows():
        blind_folder = BlindFolder.query.filter(BlindFolder.blind_name == og_blind_folder['blind_name']).first()
        if blind_folder is None:

            og_folder = folders_df[folders_df['folder_id'].str.match(og_blind_folder['folder_id'])]

            og_folder_id = og_folder['folder_id'].to_string(index=False).strip(' ')
            og_folder_dir_temp = og_folder.to_string(columns=['folder_dir'], index=False).split('/SharedX/')[-1]
            og_folder_dir = 'X:\\' + '\\'.join(og_folder_dir_temp.split('/'))

            new_folder = Folder.query.filter(Folder.folder_dir == og_folder_dir).first()
            if new_folder is None:
                print(og_folder_dir)
                continue
            og_reviewer = reviewers_df[reviewers_df['reviewer_id'].str.match(og_blind_folder['reviewer_id'])]
            new_reviewer = Reviewer.query.filter((Reviewer.first_name == og_reviewer['first_name']
                                                  .to_string(index=False).strip(' ')) and
                                                 (Reviewer.last_name == og_reviewer['first_name']
                                                  .to_string(index=False).strip(' '))).first()

            new_blind_folder = BlindFolder(folder_id=new_folder.folder_id, reviewer_id=new_reviewer.reviewer_id,
                                           blind_name=og_blind_folder['blind_name'])
            db.session.add(new_blind_folder)
            db.session.commit()

            og_all_trials = trials_df[trials_df['folder_id'].str.match(og_folder_id)]
            for inner_index, og_trial in og_all_trials.iterrows():

                og_trial_dir_temp = og_trial['trial_dir'].split('/SharedX/')[-1]
                og_trial_dir = 'X:\\' + '\\'.join(og_trial_dir_temp.split('/'))

                new_trial = Trial.query.filter(Trial.trial_dir == og_trial_dir).first()
                if new_trial is None:
                    print(og_trial_dir)

                og_all_possible_blind_trials = blind_trials_df[blind_trials_df['trial_id'].str.match(
                    og_trial['trial_id'])]

                if og_all_possible_blind_trials.shape == (1, 4):
                    og_blind_trial = og_all_possible_blind_trials.iloc[0]
                else:
                    og_blind_trial = og_all_possible_blind_trials[
                        og_all_possible_blind_trials['full_path'].str.contains(
                            f"toScore_{new_reviewer.first_name[0]}{new_reviewer.last_name[0]}"
                        )]
                blind_trial_num = int(og_blind_trial['full_path'].strip('.mp4').split('R')[-1])
                new_blind_trial = BlindTrial(blind_folder_id=new_blind_folder.blind_folder_id,
                                             reviewer_id=new_reviewer.reviewer_id,
                                             trial_id=new_trial.trial_id,
                                             folder_id=new_folder.folder_id,
                                             blind_trial_num=blind_trial_num)
                db.session.add(new_blind_trial)
                db.session.commit()


def populate_mouse_from_file(full_path):
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


def populate_reviewers_from_file(full_path):
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


def populate_experiments_from_file(full_path):
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


def populate_participant_details_from_file(full_path):
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


def populate_sessions_for_experiment(experiment_name):
    experiment = Experiment.query.filter(Experiment.experiment_name == experiment_name).first()
    for participant in experiment.participant_details:

        all_sessions = list(Path(participant.participant_dir).glob(f'{experiment.session_re}'))
        for session_dir in all_sessions:
            if Session.query.filter(Session.session_dir == session_dir) is None:
                session_num = str(session_dir).split('_')[-1]
                session_date = str(session_dir).split('_')[1]
                session_num = int(session_num.strip('RG-MISNDAT'))
                db.session.add(
                    Session(mouse_id=participant.mouse_id, experiment_id=experiment.experiment_id,
                            session_date=Date.as_date(session_date), session_dir=str(session_dir), session_num=session_num)
                )
        db.session.commit()


def populate_trials(all_trials_dir, experiment, session, folder=None):
    if experiment.folder_re is None:
        folder_id = session.session_id
        all_trial_dirs = all_trials_dir.glob(f'{experiment.trial_re}')
    else:
        folder_id = folder.folder_id
        all_trial_dirs = list(all_trials_dir.glob("*.MP4"))
    for trial_dir in all_trial_dirs:
        if trial_dir.stem == 'BackedUp' or trial_dir.stem == '.DS_Store' or trial_dir.suffix.lower() != '.mp4':
            continue
        trial = Trial.query.filter(Trial.trial_dir == str(trial_dir)).first()
        if trial is None:
            trial_num = str(trial_dir).split('_')[-1]
            trial_date = str(trial_dir).split('_')[1]
            trial_num_ext = trial_num.split('R')[-1]
            trial_num = int(trial_num_ext.split('.')[0])
            db.session.add(
                Trial(experiment_id=experiment.experiment_id, session_id=session.session_id,
                      folder_id=folder_id, trial_dir=str(trial_dir), trial_date=Date.as_date(trial_date),
                      trial_num=trial_num)
            )


def populate_trials_from_sessions(experiment_name):

    experiment = Experiment.query.filter(Experiment.experiment_name == experiment_name).first()

    for session in experiment.sessions:
        if experiment.folder_re is not None:
            # folder_re = None ==> no folders exist, just trials
            all_folder_dirs = list(Path(session.session_dir).glob(f'{experiment.folder_re}'))
            original_video_stem = '_'.join(Path(session.session_dir).name.strip('et').split('_')[:-1])
            for folder_dir in all_folder_dirs:
                folder = Folder.query.filter(Folder.folder_dir == str(folder_dir)).first()
                if folder is None:
                    folder_num = int(str(folder_dir).split(f'{experiment.folder_re.strip("*")}')[-1])
                    original_video = Path(session.session_dir).joinpath(f"{original_video_stem}_{folder_num}.MP4")
                    trial_frame_number_file = Path(session.session_dir).joinpath(
                        f"{original_video_stem}_{folder_num}.csv")
                    folder = Folder(session_id=session.session_id, folder_dir=str(folder_dir),
                                    original_video=str(original_video),
                                    trial_frame_number_file=str(trial_frame_number_file))
                    db.session.add(folder)
                    db.session.commit()
                populate_trials(all_trials_dir=folder_dir, experiment=experiment, session=session, folder=folder)
        else:
            populate_trials(session.session_dir, experiment, session)


def rebuild_empty_database(the_app):
    db.drop_all(app=the_app)
    db.create_all(app=the_app)


def populate_database_from_seed_files(seed_dir):
    populate_mouse_from_file(Path(seed_dir).joinpath('mouse.csv'))
    populate_experiments_from_file(Path(seed_dir).joinpath('experiments.csv'))
    populate_participant_details_from_file(Path(seed_dir).joinpath('participant_details.csv'))
    populate_reviewers_from_file(Path(seed_dir).joinpath('reviewers.csv'))
