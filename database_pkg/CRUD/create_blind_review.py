import os
from pathlib import Path
import random
import shutil
from shutil import Error

from database_pkg import BlindTrial, BlindFolder, Trial, Reviewer, Folder, Session
from database_pkg.Models import Experiment

# def mask_trial(trial, masked_trial_dir):
#     BlindTrial(trial.trial_id, trial.folder_id, masked_trial_dir).save_to_db()
#     try:
#         shutil.copy(trial.trial_dir, masked_trial_dir)
#         return True
#     except Error as err:
#         print(err.args[0])
#         return False
#
#
# def mask_folder(reviewer, folder):
#     # Try to load the masked_folder
#     masked_folder = BlindFolder.from_db(reviewer_id=reviewer.reviewer_id, folder_id=folder.folder_id)
#
#     if masked_folder is None:
#         # Generate a unique blind name
#         blind_name = random_string_generator(10)
#         while blind_name in get.list_all_blind_names():
#             blind_name = random_string_generator(10)
#         BlindFolder(folder.folder_id, reviewer.reviewer_id, blind_name).save_to_db()
#         masked_folder = BlindFolder.from_db(reviewer_id=reviewer.reviewer_id, folder_id=folder.folder_id)
#
#     masked_folder_dir = Path(reviewer.toScore_dir).joinpath(masked_folder.blind_name)
#     masked_folder_dir.mkdir()
#
#     for idx, trial_id in enumerate(set(get.list_trial_ids_for_folder(folder))):
#         trial_num = str(idx + 1)
#         if len(trial_num) < 2:
#             trial_num = f'0{trial_num}'
#         trial = Trial.from_db(trial_id=trial_id)
#         masked_trial_dir = masked_folder_dir.joinpath(f'{masked_folder.blind_name}_{trial_num}.mp4')
#         success = mask_trial(trial, masked_trial_dir)
#         if not success:
#             print("Issues copying")
#             break
#
#
# def copy_blind_trials(source, destination):


if __name__ == '__main__':

    experiment_name = 'dlxCKO-skilled-reaching'
    reviewer_first_name = 'Alli'
    reviewer_last_name = 'C'
    num_files = 15

    experiment = Experiment.query.filter_by(experiment_name=experiment_name).first()
    reviewer = Reviewer.query.filter_by(first_name=reviewer_first_name, last_name=reviewer_last_name).first()

    # Get status of various aspects from blind review

    all_blind_folders_not_scored = list()
    all_folders_no_scores = list()
    all_folders_not_blinded = list()

    for folder in experiment.folders:
        if len(folder.score_folders) == 0:
            all_folders_not_blinded.append(folder)
            continue

        if not any([blind_folder.is_scored() for blind_folder in folder.score_folders]):
            all_folders_no_scores.append(folder)
            continue

        for blind_folder in folder.score_folders:
            if blind_folder.is_scored():
                continue
            else:
                all_blind_folders_not_scored.append(blind_folder)

    print(f"Number Folders Not Blinded: {len(all_folders_not_blinded)}\n"
          f"Number of Blind Folders Not Scored: {len(all_blind_folders_not_scored)}\n"
          f"Number of Folders With Blind Folders But No Blind Scores: {len(all_folders_no_scores)}")

    # # Make sure all blind folders without scores have files in appropriate toScore directories
    # for blind_folder in experiment.blind_folders():
    #     if blind_folder.is_scored():
    #         continue
    #
    #     folder = Folder.query.get(blind_folder.folder_id)
    #     reviewer = Reviewer.query.get(blind_folder.reviewer_id)
    #     toScore_path = Path(reviewer.toScore_dir).joinpath(blind_folder.blind_name)
    #
    #     if reviewer.first_name == 'Krista':
    #         continue
    #
    #     if not toScore_path.exists():
    #         os.mkdir(toScore_path)
    #         for blind_trial in blind_folder.blind_trials:
    #             trial = Trial.query.get(blind_trial.trial_id)
    #             blind_trial_dir = str(
    #                 toScore_path.joinpath(
    #                     f"{blind_folder.blind_name}_{blind_trial.blind_trial_num}{Path(trial.trial_dir).suffix}"))
    #             try:
    #                 shutil.copyfile(trial.trial_dir, blind_trial_dir)
    #             except (Error, PermissionError) as err:
    #                 # print(f"shutil.copy Error: {err}\n"
    #                 #       f"Trial Directory: {trial.trial_dir}\n"
    #                 #       f"BlindTrial Directory: {blind_trial_dir}\n")
    #                 continue

    # Create Blind Folders
    folders_to_blind = random.sample(all_folders_not_blinded, num_files)
    print("Beginning to mask")
    for folder in folders_to_blind:
        blind_folder = folder.create_blind_folder(reviewer)

        blind_folder_dir = Path(reviewer.toScore_dir).joinpath(blind_folder.blind_name)
        blind_folder_dir.mkdir()

        for blind_trial in blind_folder.blind_trials:
            trial = Trial.query.get(blind_trial.trial_id)
            blind_trial_dir = str(
                blind_folder_dir.joinpath(
                    f"{blind_folder.blind_name}_{blind_trial.blind_trial_num}{Path(trial.trial_dir).suffix}"))
            try:
                shutil.copyfile(trial.trial_dir, blind_trial_dir)
            except (Error, PermissionError) as err:
                print(f"shutil.copy Error: {err}\n"
                      f"Trial Directory: {trial.trial_dir}\n"
                      f"BlindTrial Directory: {blind_trial_dir}\n")
                continue
