import pandas as pd

from data_visualization.plot_functions import plot_binary_movements

if __name__ == '__main__':
    all_scored_trials_full_path = '/Users/Krista/OneDrive - Umich/figures/all_scored_trials_df_20201203.csv'
    all_scored_trials = pd.read_csv(all_scored_trials_full_path,
                                    usecols=['eartag', 'genotype', 'birthdate', 'sex', 'session_num', 'session_date',
                                             'session_dir', 'folder_dir', 'reviewer', 'trial_dir', 'reach_score',
                                             'abnormal_movt_score', 'grooming_score'],
                                    delimiter=',')

    all_viable_trials = all_scored_trials[(all_scored_trials.reach_score != 0) &
                                          (all_scored_trials.reach_score != 6) &
                                          (all_scored_trials.reach_score != 7)]
    all_viable_trials_count = all_viable_trials.groupby(['eartag', 'genotype', 'session_num']).count()
    all_viable_trials_sum = all_viable_trials[['eartag', 'genotype', 'session_num',
                                               'abnormal_movt_score', 'grooming_score']] \
        .groupby(['eartag', 'genotype', 'session_num']) \
        .sum()

    # all_viable_trials_sum["Viable Trials"] = 0
    for eartag, genotype, session_num in all_viable_trials_count.index:
        try:
            all_viable_trials_sum.at[(eartag, genotype, session_num), "Viable Trials"] = \
                all_viable_trials_count.at[(eartag, genotype, session_num), "birthdate"]
        except KeyError:
            continue

    all_viable_trials_sum.insert(len(all_viable_trials_sum.columns), "Abnormal Movement",
                                 100 * all_viable_trials_sum['abnormal_movt_score'] /
                                 all_viable_trials_sum["Viable Trials"])
    all_viable_trials_sum.insert(len(all_viable_trials_sum.columns), "DlxGrooming",
                                 100 * all_viable_trials_sum['grooming_score'] / all_viable_trials_sum["Viable Trials"])

    plot_binary_movements("Abnormal Movement", all_viable_trials_sum, group=True)
    plot_binary_movements("DlxGrooming", all_viable_trials_sum, group=True)
    #
    # all_viable_trials_sum.reset_index(inplace=True)
    #
    # for eartag in all_viable_trials_sum.eartag.unique():
    #     subject_viable_trials = all_viable_trials_sum[all_viable_trials_sum.eartag == eartag]
    #     plot_binary_movements("Abnormal Movement", subject_viable_trials, group=False, eartag=eartag,
    #                           genotype=all_viable_trials[all_viable_trials.eartag == eartag].genotype.unique()[0])
    #     plot_binary_movements("DlxGrooming", subject_viable_trials, group=False, eartag=eartag,
    #                           genotype=all_viable_trials[all_viable_trials.eartag == eartag].genotype.unique()[0])

#     all_viable_trials_score_counts = all_viable_trials.groupby(['eartag', 'genotype', 'session_num'])['reach_score'] \
#         .value_counts() \
#         .unstack() \
#         .fillna(0)
#
#     all_viable_trials_movement_sums = all_viable_trials.groupby(['eartag', 'genotype', 'session_num']) \
#         .sum()
#
#     all_viable_trials_score_counts.reset_index(inplace=True)
#
#     all_viable_trials_score_counts.insert(len(all_viable_trials_score_counts.columns), "Viable Trials",
#                                           all_viable_trials_score_counts[1] +
#                                           all_viable_trials_score_counts[2] +
#                                           all_viable_trials_score_counts[3] +
#                                           all_viable_trials_score_counts[4] +
#                                           all_viable_trials_score_counts[5] +
#                                           all_viable_trials_score_counts[8] +
#                                           all_viable_trials_score_counts[9])
#
# # TODO Add viable trial numbers to all_viable_trials_movement_sums df
#     #  TODO calculate % ab mov & grooming
#     #  TODO group and individual graphs
#
#
#
#
#     for i in all_viable_trials_score_counts.index:
#         if all_viable_trials_score_counts.at[i, "Viable Trials"] == 0:
#             all_viable_trials_score_counts.at[i, 1] = 0
#             all_viable_trials_score_counts.at[i, 2] = 0
#             all_viable_trials_score_counts.at[i, 3] = 0
#             all_viable_trials_score_counts.at[i, 4] = 0
#             all_viable_trials_score_counts.at[i, 5] = 0
#             all_viable_trials_score_counts.at[i, 8] = 0
#             all_viable_trials_score_counts.at[i, 9] = 0
#             continue
#         all_viable_trials_score_counts.at[i, 1] = all_viable_trials_score_counts.at[i, 1] / \
#                                                   all_viable_trials_score_counts.at[i, "Viable Trials"] * 100
#         all_viable_trials_score_counts.at[i, 2] = all_viable_trials_score_counts.at[i, 2] / \
#                                                   all_viable_trials_score_counts.at[i, "Viable Trials"] * 100
#         all_viable_trials_score_counts.at[i, 3] = all_viable_trials_score_counts.at[i, 3] / \
#                                                   all_viable_trials_score_counts.at[i, "Viable Trials"] * 100
#         all_viable_trials_score_counts.at[i, 4] = all_viable_trials_score_counts.at[i, 4] / \
#                                                   all_viable_trials_score_counts.at[i, "Viable Trials"] * 100
#         all_viable_trials_score_counts.at[i, 5] = all_viable_trials_score_counts.at[i, 5] / \
#                                                   all_viable_trials_score_counts.at[i, "Viable Trials"] * 100
#         all_viable_trials_score_counts.at[i, 8] = all_viable_trials_score_counts.at[i, 8] / \
#                                                   all_viable_trials_score_counts.at[i, "Viable Trials"] * 100
#         all_viable_trials_score_counts.at[i, 9] = all_viable_trials_score_counts.at[i, 9] / \
#                                                   all_viable_trials_score_counts.at[i, "Viable Trials"] * 100
#
#     for_heatmap = list()
#     mean = all_viable_trials_score_counts.groupby(['genotype', 'session_num']).agg('mean')
#
#     for genotype, session_num in mean.index:
#         for score in [1, 2, 3, 4, 5, 8, 9]:
#             for_heatmap.append({'genotype': genotype,
#                                 'session_num': session_num,
#                                 'reach_score': score,
#                                 'percent_trials': mean.at[(genotype, session_num), f"{score}"]})
#     for_heatmap_df = pd.DataFrame.from_records(for_heatmap)
#
#     plot_reach_score_percent_heatmap(for_heatmap_df, group=True)
