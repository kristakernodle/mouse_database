from math import isnan
from pathlib import Path

import pandas as pd

from database_pkg import db, Reviewer, Session, Folder, Trial, BlindTrial, SRTrialScore, Date


def update_sessions(experiment):
    if not Path(experiment.experiment_dir).exists():
        print(f'Experiment directory does not exist: {experiment.experiment_dir}')

    participants_list = experiment.participants

    for participant in participants_list:
        sessions_search_dir = Path(participant.participant_dir).joinpath()
        if len(experiment.session_re.split('/')) > 1:
            for item in experiment.session_re.split('/')[:-1]:
                sessions_search_dir = sessions_search_dir.joinpath(item)

        sessions_in_dir = list(str(session) for session in
                               list(sessions_search_dir.glob(f'{experiment.session_re.split("/")[-1]}')))

        for session_dir in sessions_in_dir:
            session = Session.query.filter_by(session_dir=str(session_dir)).first()
            if session is None:
                session_name = Path(session_dir).name
                et_eartag, session_date, calibration_num, t_session_num = session_name.split('_')

                db.session.add(
                    Session(mouse_id=participant.mouse_id,
                            experiment_id=experiment.experiment_id,
                            session_date=Date.as_date(session_date),
                            session_dir=session_dir,
                            session_num=int(t_session_num.strip('T-MISNGDA')))
                )
                db.session.commit()


def update_folders(experiment):
    all_sessions = experiment.sessions
    for session in all_sessions:
        all_folders = Path(session.session_dir).glob(f'{experiment.folder_re}')
        for folder_dir in all_folders:
            folder = Folder.query.filter_by(folder_dir=str(folder_dir)).first()
            if folder is None:
                folder_num = folder_dir.name.strip(experiment.folder_re.strip("*"))
                original_video_stem = '_'.join(Path(session.session_dir).name.strip('et').split('_')[:-1])
                original_video = Path(session.session_dir).joinpath(f"{original_video_stem}_{folder_num}.MP4")
                trial_frame_number_file = Path(session.session_dir).joinpath(f"{original_video_stem}_{folder_num}.csv")
                db.session.add(
                    Folder(session_id=session.session_id,
                           folder_dir=str(folder_dir),
                           original_video=str(original_video),
                           trial_frame_number_file=str(trial_frame_number_file))
                )
                db.session.commit()


def update_trials(experiment):

    for session in experiment.sessions:
        all_folders = session.folders

        if len(all_folders) == 0 and experiment.folder_re is None:
            print('This case is not solved')
            exit()

        for folder in all_folders:
            all_trials = Path(folder.folder_dir).glob(f'{experiment.trial_re}')
            for trial_dir in all_trials:
                trial = Trial.query.filter_by(trial_dir=str(trial_dir)).first()

                if trial is None:
                    trial_name = trial_dir.stem
                    trial_num = trial_name.split('_')[-1].strip('RTG')

                    db.session.add(
                        Trial(experiment_id=experiment.experiment_id,
                              session_id=session.session_id,
                              folder_id=folder.folder_id,
                              trial_dir=str(trial_dir),
                              trial_date=session.session_date,
                              trial_num=int(trial_num[1:]))
                    )
                    db.session.commit()


def update_trial_scores():
    all_folders = Folder.query.all()
    for folder in all_folders:
        all_blind_folders = folder.score_folders
        for blind_folder in all_blind_folders:
            reviewer = Reviewer.query.get(blind_folder.reviewer_id)
            scored_blind_folder_path = Path(reviewer.scored_dir).joinpath(
                f"{blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")

            if scored_blind_folder_path.exists():
                all_blind_folder_scores = pd.read_csv(
                    scored_blind_folder_path,
                    usecols=['Trial', 'Score', 'Movement', 'Grooming'],
                    delimiter=',',
                    dtype={'Trial': float, 'Score': float, 'Movement': str, 'Grooming': str}
                )

                for index, scored_row in all_blind_folder_scores.iterrows():
                    if isnan(scored_row['Trial']) or isnan(scored_row['Score']):
                        continue

                    blind_trial = BlindTrial.query.filter(
                        BlindTrial.blind_folder_id == blind_folder.blind_folder_id,
                        BlindTrial.blind_trial_num == int(scored_row['Trial'])).first()

                    if blind_trial is None:
                        print('Check data integrity.')
                        break

                    if scored_row['Movement'] == '1':
                        movt = True
                    else:
                        movt = False

                    if scored_row['Grooming'] == '1':
                        groom = True
                    else:
                        groom = False

                    trial_score = SRTrialScore.query.filter(SRTrialScore.trial_id == blind_trial.trial_id,
                                                            SRTrialScore.reviewer_id == reviewer.reviewer_id).first()

                    if trial_score is None:
                        db.session.add(SRTrialScore(trial_id=blind_trial.trial_id, reviewer_id=blind_trial.reviewer_id,
                                                    reach_score=int(scored_row['Score']), abnormal_movt_score=movt,
                                                    grooming_score=groom))
                    else:
                        trial_score.reach_score = int(scored_row['Score'])
                        trial_score.abnormal_movt_score = movt
                        trial_score.grooming_score = groom

                    db.session.commit()
            else:
                print(f"Not Scored: {str(scored_blind_folder_path)}")
