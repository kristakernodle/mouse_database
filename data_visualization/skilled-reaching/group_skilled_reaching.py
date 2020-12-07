import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

import database_pkg as dbpkg
from data_visualization.plot_functions import plot_success_rate, plot_trial_numbers, plot_reach_score_percent_heatmap

palette = {"Control": 'b', "Knock-Out": 'r'}


def plot_reach_score_count_heatmap():
    for group, color in {"Control": "Blues", "Knock-Out": "Reds"}.items():
        all_viable_trials = all_scored_trials[(all_scored_trials.genotype == group) &
                                              (all_scored_trials.reach_score != 0) &
                                              (all_scored_trials.reach_score != 7) &
                                              (all_scored_trials.reach_score != 6)]

        average_score_counts = all_viable_trials.groupby(['eartag', 'session_num', 'reach_score'], as_index=False) \
            .agg('count') \
            .groupby(['session_num', 'reach_score'], as_index=False) \
            .agg('mean')

        figure, axis = plt.subplots()
        sns.set_theme(context='talk')
        sns.heatmap(average_score_counts.pivot("reach_score", "session_num", "genotype").fillna(0), cmap=color,
                    vmin=0, vmax=70, center=35)
        axis.hlines([9, 8, 5, 4, 3, 2, 1], *axis.get_xlim(), colors='grey')
        axis.vlines(list(range(1, 22)), *axis.get_ylim(), colors='grey')
        axis.spines['top'].set_visible(True)
        axis.spines['top'].set_color('grey')
        axis.spines['bottom'].set_visible(True)
        axis.spines['bottom'].set_color('grey')
        axis.spines['left'].set_visible(True)
        axis.spines['left'].set_color('grey')
        axis.spines['right'].set_visible(True)
        axis.spines['right'].set_color('grey')
        axis.set_title(f'Skilled-Reaching Reach Score By Session \n'
                       f'Average Number of Trials for {group} Group')
        axis.set_xticks(list(range(1, 22)))
        axis.set_xticklabels(list(range(1, 22)))
        axis.set(xlabel="Training Session", ylabel="Assigned Reach Score")
        plt.savefig(f'/Users/Krista/OneDrive - Umich/figures/for_committee_meeting/'
                    f'{group.lower().strip("-")}_reach_score_avgNumTrials_heatmap.png')
        plt.close()


def plot_heatmap(df):
    # df: reach_scores_by_eartag_by_session_df
    df = df[["eartag", "genotype", "session_num", "1", "2", "3", "4", "5", "8", "9", "Viable Trials"]]
    for i in df.index:
        if df.at[i, "Viable Trials"] == 0:
            df.at[i, "1"] = 0
            df.at[i, "2"] = 0
            df.at[i, "3"] = 0
            df.at[i, "4"] = 0
            df.at[i, "5"] = 0
            df.at[i, "8"] = 0
            df.at[i, "9"] = 0
            continue
        df.at[i, "1"] = df.at[i, "1"] / df.at[i, "Viable Trials"] * 100
        df.at[i, "2"] = df.at[i, "2"] / df.at[i, "Viable Trials"] * 100
        df.at[i, "3"] = df.at[i, "3"] / df.at[i, "Viable Trials"] * 100
        df.at[i, "4"] = df.at[i, "4"] / df.at[i, "Viable Trials"] * 100
        df.at[i, "5"] = df.at[i, "5"] / df.at[i, "Viable Trials"] * 100
        df.at[i, "8"] = df.at[i, "8"] / df.at[i, "Viable Trials"] * 100
        df.at[i, "9"] = df.at[i, "9"] / df.at[i, "Viable Trials"] * 100

    for_heatmap = list()
    mean = df.groupby(['genotype', 'session_num']).agg('mean')

    for genotype, session_num in mean.index:
        for score in [1, 2, 3, 4, 5, 8, 9]:
            for_heatmap.append({'genotype': genotype,
                                'session_num': session_num,
                                'reach_score': score,
                                'percent_trials': mean.at[(genotype, session_num), f"{score}"]})
    for_heatmap_df = pd.DataFrame.from_records(for_heatmap)

    plot_reach_score_percent_heatmap(for_heatmap_df, group=True)


if __name__ == '__main__':
    all_scored_trials_full_path = '/Users/Krista/OneDrive - Umich/figures/all_scored_trials_df_20201203.csv'
    all_scored_trials = pd.read_csv(all_scored_trials_full_path,
                                    usecols=['eartag', 'genotype', 'birthdate', 'sex', 'session_num', 'session_date',
                                             'session_dir', 'folder_dir', 'reviewer', 'trial_dir', 'reach_score',
                                             'abnormal_movt_score', 'grooming_score'],
                                    delimiter=',')

    reach_scores_by_session_dir = all_scored_trials.groupby(all_scored_trials.session_dir)['reach_score'] \
        .value_counts() \
        .unstack() \
        .fillna(0)

    reach_scores_by_eartag_by_session_list_dict = list()
    for session_dir, all_reach_score_counts in reach_scores_by_session_dir.iterrows():
        session = dbpkg.Session.query.filter(dbpkg.Session.session_dir == session_dir).first()
        mouse = dbpkg.Mouse.query.get(session.mouse_id)

        if mouse.genotype:
            genotype = 'Knock-Out'
        else:
            genotype = 'Control'

        reach_scores_by_eartag_by_session_list_dict.append(
            {'eartag': mouse.eartag,
             'genotype': genotype,
             'birthdate': mouse.birthdate,
             'sex': mouse.sex,
             'session_num': session.session_num,
             'session_date': session.session_date,
             'session_dir': session.session_dir,
             '0': all_reach_score_counts[0],
             '1': all_reach_score_counts[1],
             '2': all_reach_score_counts[2],
             '3': all_reach_score_counts[3],
             '4': all_reach_score_counts[4],
             '5': all_reach_score_counts[5],
             '6': all_reach_score_counts[6],
             '7': all_reach_score_counts[7],
             '8': all_reach_score_counts[8],
             '9': all_reach_score_counts[9],
             })

    reach_scores_by_eartag_by_session_df = pd.DataFrame.from_records(reach_scores_by_eartag_by_session_list_dict)

    reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "Total Trials",
                                                reach_scores_by_eartag_by_session_df.iloc[:, 7:].sum(axis=1))
    reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "Viable Trials",
                                                reach_scores_by_eartag_by_session_df.iloc[:,
                                                [8, 9, 10, 11, 12, 15, 16]].sum(axis=1))

    reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "First Success",
                                                reach_scores_by_eartag_by_session_df['1'] *
                                                100 / reach_scores_by_eartag_by_session_df['Viable Trials'])
    reach_scores_by_eartag_by_session_df['First Success'] = reach_scores_by_eartag_by_session_df[
        'First Success'].fillna(0)

    reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "Any Success",
                                                (reach_scores_by_eartag_by_session_df['1'] +
                                                 reach_scores_by_eartag_by_session_df['2']) * 100 /
                                                reach_scores_by_eartag_by_session_df['Viable Trials'])
    reach_scores_by_eartag_by_session_df['Any Success'] = reach_scores_by_eartag_by_session_df['Any Success'].fillna(0)

    plot_success_rate("First Success", reach_scores_by_eartag_by_session_df, group=True, subtitle='by Genotype')
    plot_success_rate("Any Success", reach_scores_by_eartag_by_session_df, group=True, subtitle='by Genotype')
    plot_trial_numbers("Total Trials", reach_scores_by_eartag_by_session_df)
    plot_trial_numbers("Viable Trials", reach_scores_by_eartag_by_session_df)
    # plot_reach_score_count_heatmap()
    plot_heatmap(reach_scores_by_eartag_by_session_df)
