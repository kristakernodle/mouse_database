from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from matplotlib.colors import ListedColormap
import seaborn as sns
import pandas as pd

custom_colors = {'Dlx-CKO Control': "#005AB5", "Dlx-CKO": "#DC3220"}

palette = {"Control": 'b', "Knock-Out": 'r'}
heatmap_palette = {"Control": "Blues", "Knock-Out": "Reds"}
ctrl_miss_palette = {'contact miss': 'b',
                     'no contact miss': 'b'}
ko_miss_palette = {'contact miss': 'r',
                     'no contact miss': 'r'}
ko_miss_palette = {'contact miss': '#ff0000',
                   'no contact miss': '#990000'}

cap_size = 2

blue_cmap = ListedColormap(['#0080ff', '#00407f'])
red_cmap = ListedColormap(['#ff0000', '#990000'])


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


def plot_figure1(reach_scores_by_eartag_by_session_df):

    def convert_reach_scores_df_proportion_df(genotype_reach_scores):
        proportion_list = list()
        for index, row in genotype_reach_scores.iterrows():
            row_dict = {'eartag': row.eartag,
                        'genotype': row.genotype,
                        'birthdate': row.birthdate,
                        'sex': row.sex,
                        'session_num': row.session_num}

            proportions = {'contact miss': row.prop_4,
                           'no contact miss': row.prop_5}

            for key in proportions.keys():
                this_row = dict(**row_dict,
                                **{'miss_type': key,
                                   'value': proportions[key]}
                                )
                proportion_list.append(this_row)
        return pd.DataFrame.from_records(proportion_list)

    ctrl_reach_scores = reach_scores_by_eartag_by_session_df[reach_scores_by_eartag_by_session_df['genotype'] == 'Control']
    ko_reach_scores = reach_scores_by_eartag_by_session_df[reach_scores_by_eartag_by_session_df['genotype'] == 'Knock-Out']

    ctrl_proportion_df = convert_reach_scores_df_proportion_df(ctrl_reach_scores)
    ko_proportion_df = convert_reach_scores_df_proportion_df(ko_reach_scores)

    sns.set_theme(context='paper', style="white")
    figure = plt.figure()
    w = 8
    h = 6
    figure.set_figwidth(w)
    figure.set_figheight(h)
    figure.set_dpi(600)
    figure.subplots_adjust(bottom=0.025, left=0.025, top=0.975, right=0.975)

    ax1 = plt.subplot2grid((3, 2), (0, 0))
    ax2 = plt.subplot2grid((3, 2), (0, 1))
    ax3 = plt.subplot2grid((3, 2), (1, 0), colspan=2)
    ax4 = plt.subplot2grid((3, 2), (2, 0))
    ax5 = plt.subplot2grid((3, 2), (2, 1))

    # atypicalBehavior_ax.imshow(plt.imread('/Users/Krista/OneDrive - Umich/figures/figures_ai/skilled-reaching-box.png'))
    ax1.axis("off")
    ax3.axis("off")

    sns.lineplot(ax=ax2, x="session_num", y="Any Success",
                 hue='genotype', hue_order=["Control", "Knock-Out"], palette=palette,
                 data=reach_scores_by_eartag_by_session_df, legend=True,
                 markers='o',
                 errorbar="se", err_style="bars", err_kws={'capsize': cap_size})
    ax2.set_ylim(0, 50)
    ax2.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    ax2.set_yticks([0, 10, 20, 30, 40, 50])
    ax2.get_legend().set_title('genotype')
    labels = ['control', 'knockout']
    ax2.legend(title='genotype', labels=labels)
    ax2.set(xlabel='training day', ylabel='percent success')

    sns.lineplot(ax=ax4, x="session_num", y="value",
                 hue='miss_type', style='miss_type', dashes=[(2, 2), ""], palette=ctrl_miss_palette,
                 data=ctrl_proportion_df, legend=True,
                 errorbar="se", err_style="bars", err_kws={'capsize': cap_size})
    ax4.set_ylim(0, 1)
    ax4.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    ax4.set_yticks([0, 1])
    ax4.set(title='control', xlabel='training day', ylabel='proportion of trials')
    handles_ctrl, labels_ctrl = ax4.get_legend_handles_labels()
    ax4.legend().remove()

    sns.lineplot(ax=ax5, x="session_num", y="value",
                 hue='miss_type', style='miss_type', dashes=[(2, 2), ""], palette=ko_miss_palette,
                 data=ko_proportion_df, legend=True,
                 errorbar="se", err_style="bars", err_kws={'capsize': cap_size})
    ax5.set_ylim(0, 1)
    ax5.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    ax5.set_yticks([0, 1])
    ax5.set(title='knock-out', xlabel='training day', ylabel=None)
    handles_ko, labels_ko = ax5.get_legend_handles_labels()
    ax5.legend().remove()

    legend_handles = list()
    for handle in handles_ctrl:
        handle.set_color('black')
        legend_handles.append(handle)

    ax5.legend(handles=legend_handles,
                  labels=labels_ctrl,
                  title="miss type")
    plt.tight_layout()
    plt.savefig('/Users/Krista/OneDrive - Umich/figures/figures_ai/fig1.pdf')

def plot_figure1_draft1(reach_scores_by_eartag_by_session_df):

    sns.set_theme(context='paper', style="white")

    figure = plt.figure()

    figure.subplots_adjust(bottom=0.025, left=0.025, top=0.975, right=0.975)

    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2)
    ax2 = plt.subplot2grid((3, 2), (1, 0))
    ax3 = plt.subplot2grid((3, 2), (1, 1))
    ax4 = plt.subplot2grid((3, 2), (2, 0))
    ax5 = plt.subplot2grid((3, 2), (2, 1))

    ax1.imshow(plt.imread('/Users/Krista/OneDrive - Umich/figures/figures_ai/skilled-reaching-box.png'))
    ax1.axis("off")

    sns.lineplot(ax=ax2, x="session_num", y="Any Success", hue='genotype', palette=palette,
                 data=reach_scores_by_eartag_by_session_df, legend=False)
    ax2.set_ylim(0, 50)
    ax2.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    ax2.set_yticks([0, 10, 20, 30, 40, 50])
    ax2.set(xlabel=None, ylabel='percent success')

    sns.lineplot(ax=ax3, x="session_num", y="Viable Trials", hue='genotype', palette=palette,
                 data=reach_scores_by_eartag_by_session_df, legend=False)
    ax3.set_ylim(0, 150)
    ax3.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    ax3.set_yticks([0, 50, 100, 150])
    ax3.set(xlabel=None, ylabel='number of trials')

    ctrl_reach_scores = reach_scores_by_eartag_by_session_df[reach_scores_by_eartag_by_session_df['genotype'] == 'Control']
    ko_reach_scores = reach_scores_by_eartag_by_session_df[reach_scores_by_eartag_by_session_df['genotype'] == 'Knock-Out']
    mean_ko_reach_scores = ko_reach_scores.groupby('session_num').mean()
    mean_ctrl_reach_scores = ctrl_reach_scores.groupby('session_num').mean()
    mean_ko_reach_scores = mean_ko_reach_scores.reset_index()
    mean_ctrl_reach_scores=mean_ctrl_reach_scores.reset_index()

    mean_ctrl_reach_scores.plot.line(x="session_num", y=['prop_4', 'prop_5'], ax=ax4, cmap=blue_cmap)
    ax4.set_ylim(0, 1)
    ax4.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    ax4.set_yticks([0, 1])
    ax4.set(xlabel=None, ylabel='proportion of trials')

    mean_ko_reach_scores.plot.line(x="session_num", y=['prop_4', 'prop_5'],
                                     ax=ax5, cmap=red_cmap)
    ax5.set_ylim(0, 1)
    ax5.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    ax5.set_yticks([0, 1])
    ax5.set(xlabel=None, ylabel=None)
    plt.tight_layout()
    plt.savefig('/Users/Krista/Desktop/figures/fig1.pdf')


def get_mean_sem(agg_df, columns):
    columnTups_mean = [(column.name, "mean") for column in columns]
    columnTups_sem = [(column.name, "sem") for column in columns]
    mean = agg_df[columnTups_mean].sort_index(key=lambda x: x.str.lower())
    sem = agg_df[columnTups_sem].sort_index(key=lambda x: x.str.lower())

    return mean.reset_index(), sem.reset_index()

def genotype_cleanup(df_row):
    if df_row['genotype'] == 'Dlx-CKO Control':
        return 'control'
    else:
        return 'Dlx-CKO'


class Column:
    def __init__(self, name, label, hatch=None, alpha=None):
        self.name = name
        self.label = label
        self.hatch = hatch
        self.alpha = alpha

    def __repr__(self):
        return self.name


def create_stacked_bar_chart(axis, mean_df, sem_df, ordered_columns, horizontal=False):

    if len(ordered_columns) == 1:
        error_bar = ([0, 1])
    elif len(ordered_columns) == 2:
        error_bar = ([-0.1, 0.9], [0.1, 1.1])
    elif len(ordered_columns) == 3:
        error_bar = ([-0.1, 0.9], [0, 1], [0.1, 1.1])
    else:
        error_bar = None
        print('error_bar undefined')
        breakpoint()

    x_axis = list(range(len(mean_df)))

    for index, column in enumerate(ordered_columns):
        if index == 0:
            offset = [index]*len(mean_df)
        elif index == 1:
            offset = mean_df[(ordered_columns[0].name, 'mean')]
        elif index == 2:
            offset = mean_df[(ordered_columns[0].name, 'mean')] + mean_df[(ordered_columns[1].name, 'mean')]
        else:
            offset = None
            breakpoint()

        if column.hatch is None:
                axis.bar(x_axis,
                         mean_df[(column.name, "mean")],
                         bottom=offset,
                         color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                         edgecolor='k',
                         linewidth=1,
                         alpha=column.alpha)
                axis.bar([0, 1],
                         mean_df[(column.name, "mean")],
                         bottom=offset,
                         color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                         edgecolor='k',
                         fill=False,
                         linewidth=1)
        elif column.hatch is not None:
            axis.bar([0, 1],
                     mean_df[(column.name, "mean")],
                     bottom=offset,
                     color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                     hatch=column.hatch,
                     edgecolor='w',
                     linewidth=1)
            axis.bar([0, 1],
                     mean_df[(column.name, "mean")],
                     bottom=offset,
                     color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                     edgecolor='k',
                     fill=False,
                     linewidth=1)

        for idx in [0, 1]:
            try:
                axis.errorbar(x=error_bar[index][idx],
                              y=offset[idx] + mean_df[(column.name, 'mean')][idx],
                              yerr=sem_df[(column.name, 'sem')][idx],
                              ecolor='k',
                              capsize=2)
            except TypeError:
                axis.errorbar(x=error_bar[idx],
                              y=offset[idx] + mean_df[(column.name, 'mean')][idx],
                              yerr=sem_df[(column.name, 'sem')][idx],
                              ecolor='k',
                              capsize=2)

    return axis


def format_ax(axis, ylim, yticks, ylabel, yticklabels=None, title=None, titleloc='center'):
    if yticklabels is None:
        yticklabels = yticks

    axis.set_ylim(ylim[0], ylim[1])
    axis.set_yticks(yticks)
    axis.set_yticklabels(yticklabels)
    axis.set_ylabel(ylabel)
    axis.set_xticks([0, 1])
    axis.set_xticklabels(['control', 'Dlx-CKO'], rotation='horizontal')
    axis.spines['top'].set_visible(False)
    axis.spines['right'].set_visible(False)
    axis.tick_params(axis='x', which='both', bottom=False, labelbottom=True)
    axis.set_title(title, loc=titleloc)
    return axis


def paired_bar_chart(axis, columns_dict, df, ylabel, ylim, yticks, xlabel=None, title=None, legend_on=False, bar_width=0.35):
    ordered_columns = columns_dict[axis]
    mean, sem = get_mean_sem(df, ordered_columns)
    mean = mean.set_index(('genotype',)).transpose().reset_index().set_index('level_0')
    sem = sem.set_index(('genotype',)).transpose().reset_index().set_index('level_0')

    axis_x = list(range(len(mean)))

    axis.bar([xval - bar_width / 2 for xval in axis_x],
                            mean['control'],
                            width=bar_width,
                            color=custom_colors['Dlx-CKO Control'],
                            label='control')
    axis.bar([xval + bar_width / 2 for xval in axis_x],
                            mean['Dlx-CKO'],
                            width=bar_width,
                            color=custom_colors['Dlx-CKO'],
                            label='Dlx-CKO')

    axis.errorbar(x=[xval - bar_width / 2 for xval in axis_x],
                                 y=mean['control'],
                                 yerr=sem['control'],
                                 ecolor='k',
                                 capsize=2,
                                 ls='none')
    axis.errorbar(x=[xval + bar_width / 2 for xval in axis_x],
                                 y=mean['Dlx-CKO'],
                                 yerr=sem['Dlx-CKO'],
                                 ecolor='k',
                                 capsize=2,
                                 ls='none')
    axis.set_xticks(axis_x)
    axis.set_xticklabels([column.label for column in ordered_columns], fontsize=9)
    axis.set_xlabel(xlabel, fontdict={'fontsize': 'medium'})
    axis.set_ylabel(ylabel, fontdict={'fontsize': 'small'})
    axis.set_ylim(ylim)
    axis.set_yticks(yticks)
    axis.set_yticklabels(yticks)
    axis.set_title(title, fontdict={'fontsize': 'medium'})
    axis.tick_params(axis='x', bottom=False)
    axis.spines['top'].set_visible(False)
    axis.spines['right'].set_visible(False)
    if legend_on:
        axis.legend(title=None, labels=["control", "Dlx-CKO"])
    return axis
