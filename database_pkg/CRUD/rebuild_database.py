from pathlib import Path

from database_pkg import db, app
from .reinstate_from_back_up_file import reinstate_mouse, reinstate_experiments, reinstate_participant_details, \
    reinstate_reviewers, reinstate_sessions, reinstate_folders, reinstate_trials, reinstate_blind_folders, \
    reinstate_blind_trials, reinstate_sr_trial_scores, reinstate_grooming_summary, reinstate_pasta_handling_scores, \
    reinstate_grooming_bouts, reinstate_grooming_bout_chains_full_path


def rebuild_database(back_up_dir):
    db.drop_all(app=app)
    db.create_all(app=app)

    mouse_full_path = Path(back_up_dir).joinpath('mice.csv')
    experiments_full_path = Path(back_up_dir).joinpath('experiments.csv')
    participant_details_full_path = Path(back_up_dir).joinpath('participant_details.csv')
    reviewers_full_path = Path(back_up_dir).joinpath('reviewers.csv')
    sessions_full_path = Path(back_up_dir).joinpath('sessions.csv')
    folders_full_path = Path(back_up_dir).joinpath('folders.csv')
    trials_full_path = Path(back_up_dir).joinpath('trials.csv')
    blind_folders_full_path = Path(back_up_dir).joinpath('blind_folders.csv')
    blind_trials_full_path = Path(back_up_dir).joinpath('blind_trials.csv')
    sr_trial_scores_full_path = Path(back_up_dir).joinpath('sr_trial_scores.csv')
    grooming_summary_full_path = Path(back_up_dir).joinpath('grooming_summary.csv')
    grooming_bouts_full_path = Path(back_up_dir).joinpath('grooming_bouts.csv')
    grooming_bout_chains_full_path = Path(back_up_dir).joinpath('grooming_bout_chains.csv')
    pasta_handling_scores_full_path = Path(back_up_dir).joinpath('pasta_handling_scores.csv')

    reinstate_mouse(mouse_full_path)
    reinstate_experiments(experiments_full_path)
    reinstate_participant_details(participant_details_full_path)
    reinstate_reviewers(reviewers_full_path)
    reinstate_sessions(sessions_full_path)
    reinstate_folders(folders_full_path)
    reinstate_trials(trials_full_path)
    reinstate_blind_folders(blind_folders_full_path)
    reinstate_blind_trials(blind_trials_full_path)
    reinstate_sr_trial_scores(sr_trial_scores_full_path)
    reinstate_grooming_summary(grooming_summary_full_path)
    reinstate_grooming_bouts(grooming_bouts_full_path)
    reinstate_grooming_bout_chains_full_path(grooming_bout_chains_full_path)
    reinstate_pasta_handling_scores(pasta_handling_scores_full_path)
