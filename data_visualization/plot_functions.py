import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from pathlib import Path

palette = {"Control": 'b', "Knock-Out": 'r'}
heatmap_palette = {"Control": "Blues", "Knock-Out": "Reds"}


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


def plot_success_rate(success_type, data, group: bool, subtitle=None, eartag=None,
                      save_dir='/Users/Krista/Desktop/figures/', upper_ylim=70):
    sns.set_theme(context='talk', style="darkgrid")

    figure, axis = plt.subplots()
    sns.lineplot(x="session_num", y=success_type, hue='genotype', palette=palette,
                 data=data)

    if group:
        sns.scatterplot(x="session_num", y=success_type, hue='genotype', palette=palette,
                        data=data)

    axis.set_ylim(0, upper_ylim)
    axis.set_xticks(list(range(1, 22)))
    plt.setp(axis.get_xticklabels(), rotation=90)
    axis.set(xlabel='Training Session', ylabel='Percent Success')

    title_string = f"Skilled-Reaching {success_type} Rate \n" \
                   f"{subtitle}"
    axis.set_title(title_string)

    plt.legend(title='Genotype')

    handles, labels = axis.get_legend_handles_labels()

    if len(handles) > 2:
        handles_labels = list(zip(handles, labels))
        handles_labels = [tup for tup in handles_labels if isinstance(tup[0], PathCollection)]
        handles_labels = sorted(handles_labels, key=lambda group: group[1])
        unzipped_handles_labels = list(zip(*handles_labels))
        axis.legend(unzipped_handles_labels[0], unzipped_handles_labels[1])

    if group:
        file_name = f'{"_".join(success_type.lower().split(" "))}_rate.png'
    else:
        file_name = f'{eartag}_{"_".join(success_type.lower().split(" "))}_rate.png'
    plt.subplots_adjust(bottom=0.15)
    plt.savefig(str(Path(save_dir).joinpath(file_name)))
    plt.close(figure)


def plot_trial_numbers(trial_type, data):
    sns.set_theme(context='talk', style="darkgrid")
    figure, axis = plt.subplots()
    sns.lineplot(x="session_num", y=trial_type, hue='genotype', palette=palette,
                 data=data)
    sns.scatterplot(x="session_num", y=trial_type, hue='genotype', palette=palette,
                    data=data)

    axis.set_ylim(0, 175)
    axis.set_xticks(list(range(1, 22)))
    plt.setp(axis.get_xticklabels(), rotation=90)
    axis.set_title(f'Single Pellet Skilled-Reaching \n {trial_type} Number'
                   f' by Genotype')
    axis.set(xlabel='Training Session', ylabel='Percent Success')

    plt.legend(title='Genotype')

    handles, labels = axis.get_legend_handles_labels()
    handles_labels = list(zip(handles, labels))
    handles_labels = [tup for tup in handles_labels if isinstance(tup[0], PathCollection)]
    handles_labels = sorted(handles_labels, key=lambda group: group[1])
    unzipped_handles_labels = list(zip(*handles_labels))
    axis.legend(unzipped_handles_labels[0], unzipped_handles_labels[1])

    plt.subplots_adjust(bottom=0.15, left=0.15)
    plt.savefig(
        f'/Users/Krista/OneDrive - Umich/figures/for_committee_meeting/{"_".join(trial_type.lower().split(" "))}_number.png')
    plt.close(figure)
