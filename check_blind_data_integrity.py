import database_pkg as dbpkg
import pandas as pd
import os.path
from pathlib import Path
import datetime
import shutil


def get_date_modified(full_path):
    if not Path(full_path).exists():
        print(f"File does not exist: {full_path}")
        return None
    time_modified = os.path.getmtime(full_path)
    return datetime.datetime.fromtimestamp(time_modified).date()


def remove_duplicates(duplicates_df, new_dir):
    removed_files = list()

    reviewer = dbpkg.Reviewer.query.get(pd.unique(duplicates_df['reviewer_id']))

    duplicates_df['scored_file_path'] = duplicates_df.apply(
        lambda row: os.path.join(reviewer.scored_dir,
                                 f"{row.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv"),
        axis=1)

    duplicates_df['date_last_modified'] = duplicates_df.apply(
        lambda row: get_date_modified(row['scored_file_path']),
        axis=1)

    while len(duplicates_df) > 1:
        duplicates_df.sort_values(['date_last_modified'], ascending=True, inplace=True)
        file_to_remove = duplicates_df.iloc[0]

        blind_folder_to_remove = dbpkg.BlindFolder.query.get(file_to_remove.blind_folder_id)

        try:
            shutil.move(file_to_remove.scored_file_path, new_dir)
            removed_files.append(file_to_remove)

        except shutil.Error:
            print(f'File could not be removed: {file_to_remove.scored_file_path}')

            # TODO fix this -- it will not affect my data processing, but is important for paper submission
            removed_duplicates_df = pd.concat(removed_files, axis=1, keys=[s.name for s in removed_files])
            return False, removed_duplicates_df, duplicates_df

        # Remove all associated blind_trial entries
        for blind_trial in blind_folder_to_remove.blind_trials:
            blind_trial.remove_from_db()

        # Remove blind_folder entry from database AND duplicates_df
        blind_folder_to_remove.remove_from_db()
        duplicates_df = duplicates_df.drop(duplicates_df.index[0])

    removed_duplicates_df = pd.concat(removed_files, axis=1, keys=[s.name for s in removed_files])
    return True, removed_duplicates_df, duplicates_df


new_dir = '/Volumes/SharedX/Neuro-Leventhal/data/mouseSkilledReaching/blindedScoring/scored_duplicates'

all_removed_files = list()
all_saved_files = list()

all_blind_folders_df = pd.DataFrame.from_records(
    [blind_folder_obj.as_dict() for blind_folder_obj in dbpkg.BlindFolder.query.all()])

duplicate_folders = all_blind_folders_df[all_blind_folders_df.duplicated(subset=['folder_id'])]
duplicate_folders_reviewer = duplicate_folders[duplicate_folders.duplicated(subset=['folder_id', 'reviewer_id'])]

for index, duplicate in duplicate_folders_reviewer.iterrows():
    all_duplicates = [bf_obj.as_dict() for bf_obj in
                      dbpkg.BlindFolder.query.filter(dbpkg.BlindFolder.folder_id == duplicate['folder_id']).all()]
    all_duplicates_df = pd.DataFrame.from_records(all_duplicates)

    num_reviewers = len(pd.unique(all_duplicates_df['reviewer_id']))
    if num_reviewers == 1:
        ret, removed_files_df, still_present_files_df = remove_duplicates(all_duplicates_df, new_dir)
    else:
        duplicates_same_reviewer = all_duplicates_df.groupby('reviewer_id').filter(lambda x: len(x) > 1)

        if len(duplicates_same_reviewer.drop_duplicates(subset='reviewer_id')) == 1:
            ret, removed_files_df, still_present_files_df = remove_duplicates(duplicates_same_reviewer, new_dir)
        else:
            print('Multiple reviewers with duplicate folders in the blind folders table')
            break

    if not ret:
        break

    all_removed_files.append(removed_files_df)
    all_saved_files.append(still_present_files_df)

all_removed_files_df = pd.concat(all_removed_files)
all_saved_files_df = pd.concat(all_saved_files)

all_removed_files_df.to_csv(os.path.join(new_dir, 'all_removed_files.csv'), sep=',', header=True, index=False, mode='w',
                            date_format='%m/%d/%Y')
all_saved_files_df.to_csv(os.path.join(new_dir, 'all_saved_files.csv'), sep=',', header=True, index=False, mode='w',
                          date_format='%m/%d/%Y')
