from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from matpoltlib import cm
import seaborn as sns

palette = {"Control": 'b', "Knock-Out": 'r'}
heatmap_palette = {"Control": "Blues", "Knock-Out": "Reds"}
blue_cmap = cm.get_cmap("winter")
red_cmap = cm.get_cmap("Wistia")


def plot_reach_score_percent_heatmap(df, group: bool, genotype=None, eartag=None,
                                     save_dir='/Users/Krista/Desktop/figures/'):
    """
    plot reach score percent heatmap
    :param df: pandas DataFrame; must contain three columns: session_num, reach_score, percent_trials
    :return:
    """

    def format_and_save(a_figure, a_axis, a_file_name):
        a_axis.set_xticks(list(range(1, 22)))
        a_axis.set_xticklabels(list(range(1, 22)))
        plt.setp(a_axis.get_xticklabels(), rotation=90)
        a_axis.set(xlabel="Training Session", ylabel="Assigned Reach Score")

        a_axis.hlines([a.get_text() for a in a_axis.get_yticklabels()], *a_axis.get_xlim(), colors='grey')
        a_axis.vlines([a.get_text() for a in a_axis.get_xticklabels()], *a_axis.get_ylim(), colors='grey')

        a_axis.spines['top'].set_visible(True)
        a_axis.spines['top'].set_color('grey')
        a_axis.spines['bottom'].set_visible(True)
        a_axis.spines['bottom'].set_color('grey')
        a_axis.spines['left'].set_visible(True)
        a_axis.spines['left'].set_color('grey')
        a_axis.spines['right'].set_visible(True)
        a_axis.spines['right'].set_color('grey')

        plt.subplots_adjust(bottom=0.15)
        plt.savefig(str(Path(save_dir).joinpath(a_file_name)))
        plt.close(a_figure)

    if group:
        for genotype, color in heatmap_palette.items():
            sns.set_theme(context='talk')

            figure, axis = plt.subplots()

            sns.heatmap(df[df.genotype == genotype].pivot("reach_score", "session_num", "percent_trials"), cmap=color,
                        vmin=0, vmax=100, center=50)

            axis.set_title(f'Skilled-Reaching Reach Score By Session \n'
                           f'Average Percent of Trials for {genotype} Group')
            file_name = f'{genotype.lower().strip("-")}_reach_score_heatmap.png'
            format_and_save(figure, axis, file_name)
    else:
        sns.set_theme(context='talk')

        figure, axis = plt.subplots()

        sns.heatmap(df.pivot("reach_score", "session_num", "percent_trials"), cmap=heatmap_palette[genotype],
                    vmin=0, vmax=100, center=50)

        axis.set_title(f'Skilled-Reaching Reach Score By Session \n'
                       f'Percent of Trials for {eartag} ({genotype})')
        file_name = f"{eartag}_reach_score_heatmap.png"
        format_and_save(figure, axis, file_name)


def plot_binary_movements(movement_type, data, group: bool, eartag=None, genotype=None,
                          save_dir='/Users/Krista/Desktop/figures/', upper_ylim=100):
    sns.set_theme(context='talk', style="darkgrid")
    figure, axis = plt.subplots()
    sns.lineplot(x="session_num", y=movement_type, hue='genotype', palette=palette,
                 data=data, legend=False)
    if group:
        sns.scatterplot(x="session_num", y=movement_type, hue='genotype', palette=palette,
                        data=data, legend=False)

    axis.set_ylim(0, upper_ylim)
    axis.set_xticks(list(range(1, 22)))
    plt.setp(axis.get_xticklabels(), rotation=90)
    axis.set(xlabel='Training Session', ylabel='Percent Trials')

    handles, labels = axis.get_legend_handles_labels()
    handles_labels = list(zip(handles, labels))

    if len(handles_labels) > 2:
        handles_labels = [tup for tup in handles_labels if isinstance(tup[0], PathCollection)]
        handles_labels = sorted(handles_labels, key=lambda group: group[1])
        unzipped_handles_labels = list(zip(*handles_labels))
        plt.legend(title='Genotype')
        axis.legend(unzipped_handles_labels[0], unzipped_handles_labels[1])

    if group:
        file_name = f'{"_".join(movement_type.lower().split(" "))}_presence.png'
        title_string = f"{movement_type} Behavior Presence \n" \
                       f"in Skilled-Reaching Task Performance"
    else:
        file_name = f'{eartag}_{"_".join(movement_type.lower().split(" "))}_rate.png'
        title_string = f"{movement_type} Behavior Presence \n" \
                       f"{eartag} ({genotype})"
    axis.set_title(title_string)
    plt.subplots_adjust(bottom=0.15, left=0.15)
    plt.savefig(str(Path(save_dir).joinpath(file_name)))
    plt.close(figure)


def plot_success_rate(success_type, data, group: bool, subtitle=None, eartag=None, genotype=None,
                      save_dir='/Users/Krista/Desktop/figures/', upper_ylim=70):
    sns.set_theme(context='talk', style="darkgrid")

    figure, axis = plt.subplots()
    sns.lineplot(x="session_num", y=success_type, hue='genotype', palette=palette,
                 data=data, legend=False)

    if group:
        sns.scatterplot(x="session_num", y=success_type, hue='genotype', palette=palette,
                        data=data, legend=False)

    axis.set_ylim(0, upper_ylim)
    axis.set_xticks(list(range(1, 22)))
    plt.setp(axis.get_xticklabels(), rotation=90)
    axis.set(xlabel='Training Session', ylabel='Percent Success')

    title_string = f"Skilled-Reaching {success_type} Rate \n" \
                   f"{subtitle}"
    axis.set_title(title_string)

    handles, labels = axis.get_legend_handles_labels()
    handles_labels = list(zip(handles, labels))

    if len(handles_labels) > 2:
        handles_labels = [tup for tup in handles_labels if isinstance(tup[0], PathCollection)]
        handles_labels = sorted(handles_labels, key=lambda group: group[1])
        unzipped_handles_labels = list(zip(*handles_labels))
        plt.legend(title='Genotype')
        axis.legend(unzipped_handles_labels[0], unzipped_handles_labels[1])

    if group:
        file_name = f'{"_".join(success_type.lower().split(" "))}_rate.png'
    else:
        file_name = f'{eartag}_{"_".join(success_type.lower().split(" "))}_rate.png'
    plt.subplots_adjust(bottom=0.15)
    plt.savefig(str(Path(save_dir).joinpath(file_name)))
    plt.close(figure)


def plot_trial_numbers(trial_type, data, eartag=None, genotype=None, save_dir='/Users/Krista/Desktop/figures/'):

    sns.set_theme(context='talk', style="darkgrid")
    figure, axis = plt.subplots()
    sns.lineplot(x="session_num", y=trial_type, hue='genotype', palette=palette,
                 data=data, legend=False)

    if eartag is None:
        sns.scatterplot(x="session_num", y=trial_type, hue='genotype', palette=palette,
                        data=data, legend=False)
        title_string = f"Single Pellet Skilled-Reaching \n" \
                       f"Number of {trial_type} by Session"
        file_name = f"{trial_type.lower().strip(' ')}_by_session.png"
    else:
        title_string = f"single Pellet Skilled-Reaching \n " \
                       f"Number of {trial_type} for {eartag} ({genotype})"
        file_name = f"{eartag}_{trial_type.lower().strip(' ')}_by_session.png"

    axis.set_ylim(0, 175)
    axis.set_xticks(list(range(1, 22)))
    plt.setp(axis.get_xticklabels(), rotation=90)
    axis.set_title(title_string)
    axis.set(xlabel='Training Session', ylabel='Number of Trials')

    handles, labels = axis.get_legend_handles_labels()
    handles_labels = list(zip(handles, labels))
    if len(handles_labels) > 2:
        handles_labels = [tup for tup in handles_labels if isinstance(tup[0], PathCollection)]
        handles_labels = sorted(handles_labels, key=lambda group: group[1])
        unzipped_handles_labels = list(zip(*handles_labels))
        plt.legend(title='Genotype')
        axis.legend(unzipped_handles_labels[0], unzipped_handles_labels[1])

    plt.subplots_adjust(bottom=0.15, left=0.15)
    plt.savefig(str(Path(save_dir).joinpath(file_name)))
    plt.close(figure)

if __name__ == '__main__':
    sns.set_theme(context='paper', style="white")
    figure, axis = plt.subplots(2, 2)

    sns.lineplot(ax=axis[0][0], x="session_num", y="Any Success", hue='genotype', palette=palette,
                 data=reach_scores_by_eartag_by_session_df, legend=False)
    axis[0][0].set_ylim(0, 50)
    axis[0][0].set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    axis[0][0].set_yticks([0, 10, 20, 30, 40, 50])
    axis[0][0].set(xlabel=None, ylabel='percent success')

    sns.lineplot(ax=axis[0][1], x="session_num", y="Viable Trials", hue='genotype', palette=palette,
                 data=reach_scores_by_eartag_by_session_df, legend=False)
    axis[0][1].set_ylim(0, 150)
    axis[0][1].set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    axis[0][1].set_yticks([0, 50, 100, 150])
    axis[0][1].set(xlabel=None, ylabel='number of trials')


    # sns.lineplot(ax=axis[1][0], x="session_num", y="percent_trials", hue='reach_score', palette="Blues",
    #              data=for_heatmap_df[for_heatmap_df.genotype == 'Control'], legend=False)
    # axis[1][0].set_ylim(0, 100)
    # axis[1][0].set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    # axis[1][0].set_yticks([0, 20, 40, 60, 80, 100])
    # axis[1][0].set(xlabel=None, ylabel='percent of trials')

    # plt.stackplot(x='session_num', y1=for_heatmap_df[for_heatmap_df.genotype == 'Knock-Out', for_heatmap_df['reach_score'] == 4], data=for_heatmap_df[for_heatmap_df.genotype == 'Knock-Out'], legend=False)

    ctrl_reach_scores = reach_scores_by_eartag_by_session_df[reach_scores_by_eartag_by_session_df['genotype'] == 'Control']
    ko_reach_scores = reach_scores_by_eartag_by_session_df[reach_scores_by_eartag_by_session_df['genotype'] == 'Knock-Out']
    mean_ko_reach_scores = ko_reach_scores.groupby('session_num').mean()
    mean_ctrl_reach_scores = ctrl_reach_scores.groupby('session_num').mean()
    mean_ko_reach_scores = mean_ko_reach_scores.reset_index()
    mean_ctrl_reach_scores=mean_ctrl_reach_scores.reset_index()

    mean_ctrl_reach_scores.plot.line(x="session_num", y=['prop_4', 'prop_5'], ax=axis[1][0], cmap=red_cmap)
    axis[1][0].set_ylim(0, 1)
    axis[1][0].set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    axis[1][0].set_yticks([0, 1])
    axis[1][0].set(xlabel=None, ylabel='proportion of trials')

    mean_ko_reach_scores.plot.line(x="session_num", y=['prop_4', 'prop_5'],
                                     ax=axis[1][1], cmap=blue_cmap)
    axis[1][1].set_ylim(0, 1)
    axis[1][1].set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    axis[1][1].set_yticks([0, 1])
    axis[1][1].set(xlabel=None, ylabel='proportion of trials')
    plt.tight_layout()
    plt.savefig('/Users/Krista/Desktop/figures/fig1.pdf')
