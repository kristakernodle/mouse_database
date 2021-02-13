from pathlib import Path

from database_pkg import db, app
from database_pkg.Models import (Mouse,
                                 Experiment,
                                 ParticipantDetail,
                                 Reviewer,
                                 Session,
                                 Folder,
                                 Trial,
                                 BlindFolder,
                                 BlindTrial,
                                 SRTrialScore,
                                 GroomingBout,
                                 GroomingSummary,
                                 PastaHandlingScores)


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
    pasta_handling_scores_full_path = Path(back_up_dir).joinpath('pasta_handling_scores.csv')

    Mouse.reinstate(mouse_full_path)
    Experiment.reinstate(experiments_full_path)
    ParticipantDetail.reinstate(participant_details_full_path)
    Reviewer.reinstate(reviewers_full_path)
    Session.reinstate(sessions_full_path)
    Folder.reinstate(folders_full_path)
    Trial.reinstate(trials_full_path)
    BlindFolder.reinstate(blind_folders_full_path)
    BlindTrial.reinstate(blind_trials_full_path)
    SRTrialScore.reinstate(sr_trial_scores_full_path)
    GroomingSummary.reinstate(grooming_summary_full_path)
    GroomingBout.reinstate(grooming_bouts_full_path)
    PastaHandlingScores.reinstate(pasta_handling_scores_full_path)
