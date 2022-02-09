from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

from database_pkg import Experiment

heatmap_palette = {"Control": "Blues", "Knock-Out": "Reds"}


def format_axis(axis):
    # axis.set_xticks(list(range(1, 22)))

    # axis.hlines(axis.get_yticks(), *axis.get_xlim(), colors='grey')
    # axis.vlines(axis.get_xticks(), *axis.get_ylim(), colors='grey')
    #
    # axis.set_xticklabels(list(range(1, 22)))
    # axis.set(xlabel="Training Session")

    axis.spines['top'].set_visible(True)
    axis.spines['top'].set_color('black')
    axis.spines['bottom'].set_visible(True)
    axis.spines['bottom'].set_color('black')
    axis.spines['left'].set_visible(True)
    axis.spines['left'].set_color('black')
    axis.spines['right'].set_visible(True)
    axis.spines['right'].set_color('black')


def plot_reach_score_percent_heatmap(df, group: bool, genotype=None, eartag=None,
                                     save_dir='/Users/Krista/Desktop/figures/heatmaps/'):
    """
    plot reach score percent heatmap
    :param df: pandas DataFrame; must contain three columns: session_num, reach_score, percent_trials
    :return:
    """

    file_name = 'reach_score_heatmap_20220209.pdf'

    # if group:
    matplotlib.rcParams['font.family'] = "sans-serif"
    matplotlib.rcParams['font.sans-serif'] = "Arial"
    plt.rcParams['xtick.major.pad'] = -1
    plt.rcParams['ytick.major.pad'] = -1

    sns.set_theme(context='paper', style="white")
    figure = plt.figure()
    w = 7.48031
    figure.set_figwidth(w)
    figure.set_dpi(1000)

    # Define axes
    control_ax = plt.subplot2grid((1, 2), (0, 0))
    dlx_cko_ax = plt.subplot2grid((1, 2), (0, 1))

    ax_by_genotype = {"Control": control_ax,
                      "Knock-Out": dlx_cko_ax}
    for genotype, axis_ in ax_by_genotype.items():
        plot_df = df[df.genotype == genotype].pivot("reach_score", "session_num", "percent_trials")
        plot_df.index = pd.CategoricalIndex(plot_df.index,
                                            categories=["first success", "multi try success", "drop in box",
                                                        "pellet knocked off", "pellet remained", "used tongue",
                                                        "ipsilateral paw", "tongue and paw"])
        plot_df.sort_index(level=0, inplace=True)
        sns.heatmap(plot_df,
                    cmap=heatmap_palette.get(genotype),
                    vmin=0, vmax=100, center=50,
                    ax=axis_,
                    linecolor='black',
                    linewidths=0.75,
                    cbar_kws={"shrink": 0.4})
        format_axis(axis_)

    control_ax.set_ylabel(None)
    control_ax.set_title('Control')
    dlx_cko_ax.set_title('Dlx-CKO')
    control_ax.set_xlabel('Training Day')
    dlx_cko_ax.set_xlabel('Training Day')
    dlx_cko_ax.set_yticklabels([None]*8)
    dlx_cko_ax.set_ylabel(None)
    control_ax.set_aspect(1.5)
    dlx_cko_ax.set_aspect(1.5)
    plt.tight_layout()
    plt.savefig(str(Path(save_dir).joinpath(file_name)))
    plt.close(figure)
    # else:
    #     sns.set_theme(context='talk')
    #
    #     figure, axis = plt.subplots()
    #
    #     sns.heatmap(df.pivot("reach_score", "session_num", "percent_trials"), cmap=heatmap_palette[genotype],
    #                 vmin=0, vmax=100, center=50)
    #
    #     axis.set_title(f'Skilled-Reaching Reach Score By Session \n'
    #                    f'Percent of Trials for {eartag} ({genotype})')
    #     file_name = f"{eartag}_reach_score_heatmap.png"
    #     # format_and_save(figure, axis, file_name, save_dir)


def remove_duplicate_scored_trials(scored_trials):
    duplicate_trial_dirs = scored_trials[scored_trials.duplicated(['trial_dir'])]['trial_dir']
    for dup_trial_dir in duplicate_trial_dirs:
        dup_trials = scored_trials.loc[scored_trials.trial_dir == dup_trial_dir]

        if len(dup_trials) < 2:
            break

        for name in ['Krista K', 'Alli C', 'Alli B', 'Jen M', 'Dan L']:
            if name in dup_trials.reviewer.to_list():
                scored_trials.drop(dup_trials.loc[dup_trials.reviewer != name].index.to_list())
                break
    return scored_trials


def plot_heatmap(df):
    score_map = {
        '1': "first success",
        '2': "multi try success",
        '3': "drop in box",
        '4': "pellet knocked off",
        '5': "pellet remained",
        '6': "used tongue",
        '8': "ipsilateral paw",
        '9': "tongue and paw"
    }

    # df: reach_scores_by_eartag_by_session_df
    df = df[["eartag", "genotype", "session_num", "1", "2", "3", "4", "5", "6", "8", "9", "total_trials"]]
    for i in df.index:
        if df.at[i, "total_trials"] == 0:
            df.at[i, "1"] = 0
            df.at[i, "2"] = 0
            df.at[i, "3"]= 0
            df.at[i, "4"]= 0
            df.at[i, "5"]= 0
            df.at[i, "6"]= 0
            df.at[i, "8"]= 0
            df.at[i, "9"]= 0
        else:
            df.at[i, "1"] = df.at[i, "1"] / df.at[i, "total_trials"] * 100
            df.at[i, "2"] = df.at[i, "2"] / df.at[i, "total_trials"] * 100
            df.at[i, "3"] = df.at[i, "3"] / df.at[i, "total_trials"] * 100
            df.at[i, "4"] = df.at[i, "4"] / df.at[i, "total_trials"] * 100
            df.at[i, "5"] = df.at[i, "5"] / df.at[i, "total_trials"] * 100
            df.at[i, "6"] = df.at[i, "6"] / df.at[i, "total_trials"] * 100
            df.at[i, "8"] = df.at[i, "8"] / df.at[i, "total_trials"] * 100
            df.at[i, "9"] = df.at[i, "9"] / df.at[i, "total_trials"] * 100

    for_heatmap = list()
    mean = df.groupby(['genotype', 'session_num']).agg('mean')

    for og_genotype, session_num in mean.index:

        if 'Control' in og_genotype:
            genotype = 'Control'
        else:
            genotype = 'Knock-Out'

        for score in [str(i) for i in [1, 2, 3, 4, 5, 6, 8, 9]]:
            for_heatmap.append({'genotype': genotype,
                                'session_num': session_num,
                                'reach_score': score_map.get(score),
                                'percent_trials': mean.at[(og_genotype, session_num), f"{score}"]})
    for_heatmap_df = pd.DataFrame.from_records(for_heatmap)

    plot_reach_score_percent_heatmap(for_heatmap_df, group=True)


if __name__ == '__main__':
    experiment = Experiment.get_by_name('dlxCKO-skilled-reaching')

    all_scored_trials = experiment.get_all_scored_trials()

    all_scored_trials['reviewer'] = f"{all_scored_trials['first_name']} {all_scored_trials['last_name']}"

    all_scored_trials = remove_duplicate_scored_trials(all_scored_trials)

    reach_scores_by_session = all_scored_trials.groupby(['session_dir', 'session_num', 'eartag', 'genotype'])[
        'reach_score'] \
        .value_counts() \
        .unstack() \
        .fillna(0) \
        .reset_index()

    reach_scores_by_session = reach_scores_by_session.rename(
        columns={val: str(val) for val in reach_scores_by_session.columns.to_list()})

    reach_scores_by_session['total_trials'] = sum([reach_scores_by_session[str(i)] for i in [1, 2, 3, 4, 5, 6, 8, 9]])

    # reach_scores_by_session = reach_scores_by_session.rename(
    #     columns={
    #         '0': "no pellet",
    #         '1': "first success",
    #         '2': "multi try success",
    #         '3': "drop in box",
    #         '4': "pellet knocked off",
    #         '5': "pellet remained",
    #         '6': "used tongue",
    #         '7': "no attempt",
    #         '8': "ipsilateral paw",
    #         '9': "tongue and paw"
    #     }
    # )

    # reach_scores_by_eartag_by_session_df = pd.DataFrame.from_records(reach_scores_by_eartag_by_session_list_dict)
    #
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "Total Trials",
    #                                             reach_scores_by_eartag_by_session_df.iloc[:, 7:].sum(axis=1))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "Viable Trials",
    #                                             reach_scores_by_eartag_by_session_df.iloc[:,
    #                                             [8, 9, 10, 11, 12, 15, 16]].sum(axis=1))
    #
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "First Success",
    #                                             reach_scores_by_eartag_by_session_df['1'] *
    #                                             100 / reach_scores_by_eartag_by_session_df['Viable Trials'])
    # reach_scores_by_eartag_by_session_df['First Success'] = reach_scores_by_eartag_by_session_df[
    #     'First Success'].fillna(0)
    #
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "Any Success",
    #                                             (reach_scores_by_eartag_by_session_df['1'] +
    #                                              reach_scores_by_eartag_by_session_df['2']) * 100 /
    #                                             reach_scores_by_eartag_by_session_df['Viable Trials'])
    # reach_scores_by_eartag_by_session_df['Any Success'] = reach_scores_by_eartag_by_session_df['Any Success'].fillna(0)
    #
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_0', (
    #             reach_scores_by_eartag_by_session_df['0'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_1', (
    #             reach_scores_by_eartag_by_session_df['1'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_2', (
    #             reach_scores_by_eartag_by_session_df['2'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_3', (
    #             reach_scores_by_eartag_by_session_df['3'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_4', (
    #             reach_scores_by_eartag_by_session_df['4'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_5', (
    #             reach_scores_by_eartag_by_session_df['5'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_6', (
    #             reach_scores_by_eartag_by_session_df['6'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_7', (
    #             reach_scores_by_eartag_by_session_df['7'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_8', (
    #             reach_scores_by_eartag_by_session_df['8'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    # reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_9', (
    #             reach_scores_by_eartag_by_session_df['9'] / reach_scores_by_eartag_by_session_df['Total Trials']))
    #
    # reach_scores_by_eartag_by_session_df['prop_0'] = reach_scores_by_eartag_by_session_df['prop_0'].fillna(0)
    # reach_scores_by_eartag_by_session_df['prop_1'] = reach_scores_by_eartag_by_session_df['prop_1'].fillna(0)
    # reach_scores_by_eartag_by_session_df['prop_2'] = reach_scores_by_eartag_by_session_df['prop_2'].fillna(0)
    # reach_scores_by_eartag_by_session_df['prop_3'] = reach_scores_by_eartag_by_session_df['prop_3'].fillna(0)
    # reach_scores_by_eartag_by_session_df['prop_4'] = reach_scores_by_eartag_by_session_df['prop_4'].fillna(0)
    # reach_scores_by_eartag_by_session_df['prop_5'] = reach_scores_by_eartag_by_session_df['prop_5'].fillna(0)
    # reach_scores_by_eartag_by_session_df['prop_6'] = reach_scores_by_eartag_by_session_df['prop_6'].fillna(0)
    # reach_scores_by_eartag_by_session_df['prop_7'] = reach_scores_by_eartag_by_session_df['prop_7'].fillna(0)
    # reach_scores_by_eartag_by_session_df['prop_8'] = reach_scores_by_eartag_by_session_df['prop_8'].fillna(0)
    # reach_scores_by_eartag_by_session_df['prop_9'] = reach_scores_by_eartag_by_session_df['prop_9'].fillna(0)

    # plot_figure1(reach_scores_by_eartag_by_session_df)
    #
    # plot_success_rate("First Success", reach_scores_by_eartag_by_session_df, group=True, subtitle='by Genotype')
    # plot_success_rate("Any Success", reach_scores_by_eartag_by_session_df, group=True, subtitle='by Genotype')
    # plot_trial_numbers("Total Trials", reach_scores_by_eartag_by_session_df)
    # plot_trial_numbers("Viable Trials", reach_scores_by_eartag_by_session_df)
    plot_heatmap(reach_scores_by_session)
