import database_pkg as dbpkg
import pandas as pd
import os.path
from pathlib import Path
import datetime


def get_date_modified(full_path):
    if not Path(full_path).exists():
        print(f"File does not exist: {full_path}")
        return None
    time_modified = os.path.getmtime(full_path)
    return datetime.datetime.fromtimestamp(time_modified).date()


def remove_duplicates(duplicates_df):
    removed_files = list()
    reviewer = dbpkg.Reviewer.query.get(pd.unique(duplicates_df['reviewer_id']))

    duplicates_df['scored_file_path'] = duplicates_df.apply(lambda row: os.path.join(reviewer.scored_dir,
                                                                                     f"{row.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv"),
                                                            axis=1)

    duplicates_df['date_last_modified'] = duplicates_df.apply(lambda row: get_date_modified(row['scored_file_path']),
                                                              axis=1)

    while len(duplicates_df) > 1:
        duplicates_df.sort_values(['date_last_modified'], ascending=True, inplace=True)
        file_to_remove = duplicates_df.iloc[0]
        removed_files.append(file_to_remove)


    if ret is False:
        print('WHAT HAPPENED')
        return False, None
    return True, file_creation_dates_df


# sr_experiment = dbpkg.Experiment.query.filter(dbpkg.Experiment.experiment_name == 'skilled-reaching').first()

all_blind_folders_df = pd.DataFrame.from_records(
    [blind_folder_obj.as_dict() for blind_folder_obj in dbpkg.BlindFolder.query.all()]
)

duplicate_folders = all_blind_folders_df[all_blind_folders_df.duplicated(subset=['folder_id'])]
duplicate_folders_reviewer = duplicate_folders[duplicate_folders.duplicated(subset=['folder_id', 'reviewer_id'])]

for index, duplicate in duplicate_folders_reviewer.iterrows():
    all_duplicates = [bf_obj.as_dict() for bf_obj in
                      dbpkg.BlindFolder.query.filter(dbpkg.BlindFolder.folder_id == duplicate['folder_id']).all()]
    all_duplicates_df = pd.DataFrame.from_records(all_duplicates)

    num_reviewers = len(pd.unique(all_duplicates_df['reviewer_id']))
    if num_reviewers == 1:
        ret, file_creation_dates_df = remove_duplicates(all_duplicates_df)
    else:
        duplicates_same_reviewer = all_duplicates_df.groupby('reviewer_id').filter(lambda x: len(x) > 1)

        if len(duplicates_same_reviewer.drop_duplicates(subset='reviewer_id')) == 1:
            ret, file_creation_dates_df = remove_duplicates(duplicates_same_reviewer)
        else:
            print('Multiple reviewers with duplicate folders in the blind folders table')
            break
