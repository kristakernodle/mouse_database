from sqlalchemy import exists, and_
from random import sample
from pathlib import Path
from shutil import copyfile, Error

from .Models import (Experiment, Reviewer, Session, Folder, BlindFolder, Trial,)


def create_blind_folders(experiment_name, reviewer_name, num_files=1):
    experiment = Experiment.get_by_name(experiment_name)
    reviewer_first_name, reviewer_last_name = reviewer_name.split(' ')
    reviewer = Reviewer.query.filter_by(first_name=reviewer_first_name, last_name=reviewer_last_name).first()

    # Folders with no BlindFolders
    all_folders_not_blinded = Folder.query\
        .join(Session, Folder.session_id == Session.session_id)\
        .filter(Session.experiment_id == experiment.experiment_id)\
        .filter(~exists()
                .where(and_(Folder.folder_id == BlindFolder.folder_id, Folder.session_id == Session.session_id)))\
        .all()

    # Select Folders to blind
    folders_to_blind = sample(all_folders_not_blinded, num_files)

    for folder in folders_to_blind:

        blind_folder = folder.create_blind_folder(reviewer)
        blind_folder_dir = Path(reviewer.toScore_dir).joinpath(blind_folder.blind_name)
        blind_folder_dir.mkdir()

        for blind_trial in blind_folder.blind_trials:
            trial = Trial.query.get(blind_trial.trial_id)
            blind_trial_dir = str(
                blind_folder_dir.joinpath(
                    f"{blind_folder.blind_name}_{blind_trial.blind_trial_num}.mp4"))
            try:
                copyfile(trial.trial_dir, blind_trial_dir)
            except (Error, PermissionError) as err:
                print(f"shutil.copy Error: {err}\n"
                      f"Trial Directory: {trial.trial_dir}\n"
                      f"BlindTrial Directory: {blind_trial_dir}\n")
                continue
