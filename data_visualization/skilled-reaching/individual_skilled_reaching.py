import pandas as pd
from data_visualization.plot_functions import plot_success_rate, plot_trial_numbers, plot_reach_score_percent_heatmap


all_scored_trials_full_path = '/Users/Krista/Desktop/figures/reach_scores_by_eartag_by_session_df_20220130.csv.csv'
all_scored_trials = pd.read_csv(all_scored_trials_full_path,
                                usecols=['eartag', 'genotype', 'birthdate', 'sex', 'session_num', 'session_date',
                                         'session_dir', 'folder_dir', 'reviewer', 'trial_dir', 'reach_score',
                                         'abnormal_movt_score', 'grooming_score'],
                                delimiter=',')
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
    for session_num in range(1, 22):
        for reach_score in range(1, 9):
            try:
                percent = summary_reach_scores.at[session_num, reach_score] * 100 \
                          / summary_reach_scores.at[session_num, "Viable Trials"]
            except ZeroDivisionError:
                percent = 0
            except KeyError:
                percent = 0

            try:
                score_value_counts_individual = {"eartag": eartag,
                                                 "session_num": session_num,
                                                 "genotype": trials_for_eartag.iloc[0].genotype,
                                                 "reach_score": reach_score,
                                                 "Total Trials": summary_reach_scores.at[session_num, "Total Trials"],
                                                 "Viable Trials": summary_reach_scores.at[session_num, "Viable Trials"],
                                                 "percent_trials": percent}
            except KeyError:
                try:
                    score_value_counts_individual = {"eartag": eartag,
                                                     "session_num": session_num,
                                                     "genotype": trials_for_eartag.iloc[0].genotype,
                                                     "reach_score": reach_score,
                                                     "Total Trials": summary_reach_scores.at[
                                                         session_num, "Total Trials"],
                                                     "Viable Trials": 0,
                                                     "percent_trials": percent}
                except KeyError:
                    score_value_counts_individual = {"eartag": eartag,
                                                     "session_num": session_num,
                                                     "genotype": trials_for_eartag.iloc[0].genotype,
                                                     "reach_score": reach_score,
                                                     "Total Trials": 0,
                                                     "Viable Trials": 0,
                                                     "percent_trials": percent}
            score_value_counts_list.append(score_value_counts_individual)

    score_value_counts = pd.DataFrame.from_records(score_value_counts_list)
    summary_reach_scores["genotype"] = genotype
    #
    # plot_success_rate("First Success", summary_reach_scores, group=False, subtitle=f"{eartag}, Genotype: {genotype}", eartag=eartag,
    #                   genotype=genotype, save_dir='/Users/Krista/Desktop/figures/', upper_ylim=70)
    # plot_success_rate("Any Success", summary_reach_scores, group=False, subtitle=f"{eartag}, Genotype: {genotype}", eartag=eartag,
    #                   save_dir='/Users/Krista/Desktop/figures/', upper_ylim=70)
    #
    # plot_trial_numbers("Total Trials", score_value_counts, eartag, genotype)
    # plot_trial_numbers("Viable Trials", score_value_counts, eartag, genotype)

    for_heatmap = list()
    for i in range(0, len(score_value_counts)):
        if score_value_counts.at[i, "reach_score"] in [0, 6, 7]:
            continue
        for_heatmap.append({'genotype': genotype,
                            'session_num': score_value_counts.at[i, "session_num"],
                            'reach_score': score_value_counts.at[i, "reach_score"],
                            'percent_trials': score_value_counts.at[i, "percent_trials"]})
    for_heatmap_df = pd.DataFrame.from_records(for_heatmap)
    plot_reach_score_percent_heatmap(for_heatmap_df, group=False, genotype=genotype, eartag=eartag)

