import pandas as pd
from data_visualization.plot_functions import plot_success_rate, plot_trial_numbers, plot_reach_score_percent_heatmap


all_scored_trials_full_path = '/Users/Krista/OneDrive - Umich/figures/all_scored_trials_df_20201203.csv'
all_scored_trials = pd.read_csv(all_scored_trials_full_path,
                                usecols=['eartag', 'genotype', 'birthdate', 'sex', 'session_num', 'session_date',
                                         'session_dir', 'folder_dir', 'reviewer', 'trial_dir', 'reach_score',
                                         'abnormal_movt_score', 'grooming_score'],
                                delimiter=',')

all_score_counts = list()
for eartag in all_scored_trials.eartag.unique():
    trials_for_eartag = all_scored_trials[all_scored_trials.eartag == eartag]

    genotype = trials_for_eartag.genotype.unique()[0]

    summary_reach_scores = trials_for_eartag.groupby(trials_for_eartag.session_num)['reach_score'] \
        .value_counts() \
        .unstack() \
        .fillna(0)

    summary_reach_scores.insert(summary_reach_scores.shape[1], "Total Trials",
                                summary_reach_scores.iloc[:, :].sum(axis=1))

    for i in range(1, 10):
        try:
            summary_reach_scores.columns.get_loc(i)
        except KeyError:
            summary_reach_scores[i] = 0

    summary_reach_scores.insert(summary_reach_scores.shape[1], "Viable Trials",
                                summary_reach_scores[1] + summary_reach_scores[2] + summary_reach_scores[3] +
                                summary_reach_scores[4] + summary_reach_scores[5] + summary_reach_scores[8] +
                                summary_reach_scores[9])

    summary_reach_scores.insert(summary_reach_scores.shape[1], "First Success",
                                100 * summary_reach_scores[1] / summary_reach_scores["Viable Trials"])

    summary_reach_scores.insert(summary_reach_scores.shape[1], "Any Success",
                                100 * (summary_reach_scores[1] + summary_reach_scores[2]) /
                                summary_reach_scores["Viable Trials"])

    summary_reach_scores["First Success"].fillna(0)
    summary_reach_scores["Any Success"].fillna(0)

    score_value_counts_list = list()
    success_rate_list = list()
    for session_num in range(1, 22):
        try:
            success_rate_list.append({"eartag": eartag,
                                      "session_num": session_num,
                                      "genotype": genotype,
                                      "Total Videos": summary_reach_scores.loc[session_num]["Total Videos"],
                                      "Viable Trials": summary_reach_scores.loc[session_num]["Viable Trials"],
                                      "First Success": summary_reach_scores.loc[session_num]["First Success"],
                                      "Any Success": summary_reach_scores.loc[session_num]["Any Success"]})
        except KeyError:
            pass

        viable_trials = trials_for_eartag[(trials_for_eartag.session_num == session_num) &
                                           (trials_for_eartag.reach_score != 0) &
                                           (trials_for_eartag.reach_score != 6) &
                                           trials_for_eartag.reach_score != 7]

        for reach_score in range(1, 9):
            viable_reach_score = viable_trials[viable_trials.reach_score == reach_score]
            try:
                percent = len(viable_reach_score) * 100 / len(viable_trials)
            except ZeroDivisionError:
                percent = 0
            score_value_counts_individual = {"eartag": eartag,
                                             "session_num": session_num,
                                             "genotype": trials_for_eartag.iloc[0].genotype,
                                             "reach_score": reach_score,
                                             "Number of Trials": len(viable_reach_score),
                                             "percent_trials": percent}
            score_value_counts_list.append(score_value_counts_individual)
            all_score_counts.append(score_value_counts_individual)

    success_rate = pd.DataFrame.from_records(success_rate_list)
    score_value_counts = pd.DataFrame.from_records(score_value_counts_list)

    plot_success_rate("First Success", success_rate, group=False, subtitle=f"{eartag}, Genotype: {genotype}", eartag=eartag,
                      save_dir='/Users/Krista/Desktop/figures/', upper_ylim=70)

    plot_reach_score_percent_heatmap(score_value_counts, group=False, genotype=genotype, eartag=eartag)
