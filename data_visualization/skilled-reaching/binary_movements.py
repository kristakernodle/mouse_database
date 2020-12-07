import pandas as pd

import database_pkg as dbpkg
from data_visualization.plot_functions import plot_binary_movements

if __name__ == '__main__':
    all_scored_trials_full_path = '/Users/Krista/OneDrive - Umich/figures/all_scored_trials_df_20201203.csv'
    all_scored_trials = pd.read_csv(all_scored_trials_full_path,
                                    usecols=['eartag', 'genotype', 'birthdate', 'sex', 'session_num', 'session_date',
                                             'session_dir', 'folder_dir', 'reviewer', 'trial_dir', 'reach_score',
                                             'abnormal_movt_score', 'grooming_score'],
                                    delimiter=',')

    count_data = all_scored_trials.groupby(['eartag', 'genotype', 'session_num']).count()
    sum_movement_data = all_scored_trials[['eartag', 'genotype', 'session_num',
                                           'abnormal_movt_score', 'grooming_score']]\
        .groupby(['eartag', 'genotype', 'session_num'])\
        .sum('abnormal_movt_score')\

    for_plotting = list()
    for i in count_data.index:
        eartag, genotype, session_num = i
        total_trials = count_data.at[i, 'birthdate']
        for_plotting.append({'eartag': eartag,
                             'genotype': genotype,
                             'session_num': session_num,
                             'Total Trials': total_trials,
                             'Abnormal Movement': sum_movement_data.at[(eartag, genotype, session_num),
                                                                       'abnormal_movt_score'],
                             'Grooming': sum_movement_data.at[(eartag, genotype, session_num),
                                                              'grooming_score']})

    for_plotting_df = pd.DataFrame.from_records(for_plotting)

    plot_binary_movements("Abnormal Movement", for_plotting_df, group=True, upper_ylim=50)
    plot_binary_movements("Grooming", for_plotting_df, group=True)



