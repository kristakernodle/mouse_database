import pandas as pd
from pathlib import Path
from math import isnan

from database_pkg import db, Reviewer, Folder, BlindTrial, app, SRTrialScore
from database_pkg.CRUD.reinstate_from_back_up_file import reinstate_mouse, reinstate_experiments, \
    reinstate_participant_details, reinstate_reviewers, reinstate_sessions, \
    reinstate_folders, reinstate_trials, reinstate_blind_folders, \
    reinstate_blind_trials



def populate_trial_scores():
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

                    blind_trial = BlindTrial.query.filter(BlindTrial.blind_folder_id == blind_folder.blind_folder_id,
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


def rebuild_database(back_up_dir):
    db.drop_all(app=app)
    db.create_all(app=app)

    mouse_full_path = Path(back_up_dir).joinpath('mouse.csv')
    experiments_full_path = Path(back_up_dir).joinpath('experiments.csv')
    participant_details_full_path = Path(back_up_dir).joinpath('participant_details.csv')
    reviewers_full_path = Path(back_up_dir).joinpath('reviewers.csv')
    sessions_full_path = Path(back_up_dir).joinpath('sessions.csv')
    folders_full_path = Path(back_up_dir).joinpath('folders.csv')
    trials_full_path = Path(back_up_dir).joinpath('trials.csv')
    blind_folders_full_path = Path(back_up_dir).joinpath('blind_folders.csv')
    blind_trials_full_path = Path(back_up_dir).joinpath('blind_trials.csv')

    reinstate_mouse(mouse_full_path)
    reinstate_experiments(experiments_full_path)
    populate_participant_details_from_file(participant_details_full_path)
    reinstate_reviewers(reviewers_full_path)
    reinstate_sessions(sessions_full_path)
    reinstate_folders(folders_full_path)
    reinstate_trials(trials_full_path)
    reinstate_blind_folders(blind_folders_full_path)
    reinstate_blind_trials(blind_trials_full_path)
