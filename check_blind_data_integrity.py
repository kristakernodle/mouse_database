import database_pkg as dbpkg
import pandas as pd
import os.path
from pathlib import Path
import datetime
import shutil
from random import choice


def get_date_modified(blind_folder):
    reviewer = dbpkg.Reviewer.query.get(blind_folder.reviewer_id)
    full_path = Path(reviewer.scored_dir).joinpath(
        f"{blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")
    if not full_path.exists():
        print(f"File does not exist: {full_path}")
        return None
    time_modified = os.path.getmtime(full_path)
    return datetime.datetime.fromtimestamp(time_modified).date()


def remove_blind_folder_and_associated_trials(blind_folder):
    all_blind_trials = blind_folder.blind_trials
    for blind_trial in all_blind_trials:
        blind_trial.remove_from_db()
    blind_folder.remove_from_db()


if __name__ == '__main__':
    scored_dup_dir = '/Volumes/SharedX/Neuro-Leventhal/data/mouseSkilledReaching/blindedScoring/scored_duplicates'
    lost_keys_dir = '/Users/Krista/Desktop/lost_keys'

    all_duplicates_for_removal = list()
    all_duplicates_to_keep = list()

    all_blind_folders_df = pd.DataFrame.from_records(
        [blind_folder_obj.as_dict() for blind_folder_obj in dbpkg.BlindFolder.query.all()])

    duplicate_folder_reviewer = all_blind_folders_df[all_blind_folders_df.duplicated(subset=['folder_id', 'reviewer_id'])][['folder_id', 'reviewer_id']]

    if len(duplicate_folder_reviewer) == 0:
        print("No duplicates found.")
        exit()

    for index, duplicate_pair in duplicate_folder_reviewer.iterrows():
        all_duplicates_for_pair = dbpkg.BlindFolder.query.filter(
            dbpkg.BlindFolder.folder_id == duplicate_pair.folder_id,
            dbpkg.BlindFolder.reviewer_id == duplicate_pair.reviewer_id).all()

        # Check to see if any are already scored vs not already scored
        scored_list = [blind_folder.is_scored() for blind_folder in all_duplicates_for_pair]
        if len(scored_list) < 2:
            pass

        if all(scored_list):

            # If all are already scored, choose the one modified most recently
            all_duplicates_for_pair_date_modified_list_dicts = []
            for blind_folder in all_duplicates_for_pair:
                blind_folder_dict = blind_folder.as_dict()
                blind_folder_dict.update({'date_modified': get_date_modified(blind_folder)})
                all_duplicates_for_pair_date_modified_list_dicts.append(blind_folder_dict)
            all_duplicates_for_pair_date_modified_list_dicts.sort(key=lambda i: i['date_modified'])
            # @note: Sorts by ascending date modified

            all_duplicates_for_removal.append(all_duplicates_for_pair_date_modified_list_dicts[:-1])
            all_duplicates_to_keep.append(all_duplicates_for_pair_date_modified_list_dicts[-1])

        elif dbpkg.utilities.exactly_one_true(scored_list):
            # If only one is scored, removed the unscored blind folders
            for blind_folder in all_duplicates_for_pair:
                if blind_folder.is_scored():
                    continue

                # Check if folder has been created in reviewer's toScore folder:
                reviewer = dbpkg.Reviewer.query.get(blind_folder.reviewer_id)
                blind_folder_to_score_path = Path(reviewer.toScore_dir).joinpath(blind_folder.blind_name)
                if not blind_folder_to_score_path.exists():
                    # If not: remove all blind_trials and blind_folder from database
                    remove_blind_folder_and_associated_trials(blind_folder)
                else:
                    # If so: remove the blind_folder from the toScore directory
                    try:
                        shutil.rmtree(str(blind_folder_to_score_path))
                        remove_blind_folder_and_associated_trials(blind_folder)
                    except shutil.Error:
                        pass

        elif dbpkg.utilities.all_false(scored_list):
            # @note: I have had no use of this case, so I put code in for what I would do, but I have not tested it
            print('No blind_folders scored! This case has not been tested')
            continue
            # paths_exist = list()
            # for blind_folder in all_duplicates_for_pair:
            #     # Check if folder has been created in reviewer's toScore folder:
            #     reviewer = dbpkg.Reviewer.query.get(blind_folder.reviewer_id)
            #     blind_folder_to_score_path = Path(reviewer.toScore_dir).joinpath(blind_folder.blind_name)
            #     paths_exist.append(blind_folder_to_score_path.exists())
            # if all(paths_exist):
            #     for blind_folder in all_duplicates_for_pair[:-1]:
            #         reviewer = dbpkg.Reviewer.query.get(blind_folder.reviewer_id)
            #         blind_folder_to_score_path = Path(reviewer.toScore_dir).joinpath(blind_folder.blind_name)
            #         try:
            #             shutil.rmtree(str(blind_folder_to_score_path))
            #             remove_blind_folder_and_associated_trials(blind_folder)
            #         except shutil.Error:
            #             pass

        else:
            # Have no needed this case; did not write anything useful
            print('More than one but not all blind_folders scored! This case has not been tested')
            continue

    blind_folders_no_trials = 0
    blind_folders_with_trials = 0
    for blind_folder_dict in all_duplicates_to_keep:
        blind_folder = dbpkg.BlindFolder.query.get(blind_folder_dict['blind_folder_id'])
        folder = dbpkg.Folder.query.get(blind_folder_dict['folder_id'])
        if len(folder.trials) != len(blind_folder.blind_trials):
            reviewer = dbpkg.Reviewer.query.get(blind_folder_dict['reviewer_id'])
            blind_folder_scored_path = Path(reviewer.scored_dir).joinpath(f"{blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")
            try:
                shutil.move(str(blind_folder_scored_path), lost_keys_dir)
                remove_blind_folder_and_associated_trials(blind_folder)
            except shutil.Error:
                continue

    for blind_folder_list in all_duplicates_for_removal:
        for blind_folder_dict in blind_folder_list:
            blind_folder = dbpkg.BlindFolder.query.get(blind_folder_dict['blind_folder_id'])
            reviewer = dbpkg.Reviewer.query.get(blind_folder.reviewer_id)
            blind_folder_scored_path = Path(reviewer.scored_dir).joinpath(
                f"{blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")
            try:
                shutil.move(str(blind_folder_scored_path), scored_dup_dir)
                remove_blind_folder_and_associated_trials(blind_folder)
            except shutil.Error:
                continue