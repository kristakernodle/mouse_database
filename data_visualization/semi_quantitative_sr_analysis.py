import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from typing import List

from data_visualization.plot_functions import Column, get_mean_sem

custom_colors = {'Control': "#005AB5", "Dlx-CKO": "#DC3220"}
bar_width = 0.35


def create_paired_bars(axis, x_range: List, mean, sem, bar_width_=bar_width):
    axis.barh([xval - bar_width_ / 2 for xval in x_range],
              mean['Control'],
              height=bar_width_,
              color=custom_colors['Control'],
              xerr=sem['Control'],
              capsize=2)
    axis.barh([xval + bar_width_ / 2 for xval in x_range],
              mean['Knock-Out'],
              height=bar_width_,
              color=custom_colors['Dlx-CKO'],
              xerr=sem['Knock-Out'],
              capsize=2)
    #
    # axis.errorbar(x=[xval - bar_width / 2 for xval in x_range],
    #                              y=mean['Control'],
    #                              yerr=sem['Control'],
    #                              ecolor='k',
    #                              capsize=2,
    #                              ls='none')
    # axis.errorbar(x=[xval + bar_width / 2 for xval in x_range],
    #                              y=mean['Knock-Out'],
    #                              yerr=sem['Knock-Out'],
    #                              ecolor='k',
    #                              capsize=2,
    #                              ls='none')

    axis.invert_yaxis()

    axis.set_xlim(0, 0.5)
    axis.set_xticks([0, 0.5])
    axis.set_xticklabels([0, 0.5])
    axis.set_xlabel('Movement Score')
    #
    # axis.set_xticks(x_range)
    # axis.set_xticklabels([column.label for column in orderedColumns], fontsize=9)

    axis.spines['top'].set_visible(False)
    axis.spines['right'].set_visible(False)


if __name__ == '__main__':
    submovement_scores = pd.read_csv('/Users/Krista/Desktop/semiQuant/semi_quant_scoring.csv')

    submovement_scores = submovement_scores.rename(columns={"limb_lift": "limb lift",
                                                            "digits_close": "digits close",
                                                            "digits_extend": "digits extend and open",
                                                            "supinate_i": "supinate I",
                                                            "supinate_ii": "supinate II"})

    early_submovement_scores = submovement_scores.loc[submovement_scores['group'] == 'early']
    late_submovement_scores = submovement_scores.loc[submovement_scores['group'] == 'late']

    ordered_columns = [Column('orient', label="orient"),
                       Column('limb lift', label='limb lift'),
                       Column('digits close', label="digits close"),
                       Column('aim', label="aim"),
                       Column('advance', label="advance"),
                       Column('digits extend and open', label="digits extend & open"),
                       Column('pronate', label='pronate'),
                       Column('grasp', label='grasp'),
                       Column('supinate I', label='supinate I'),
                       Column('supinate II', label='supinate II'),
                       Column('release', label='release'),
                       Column('replace', label='replace')]

    early_submovement_agg = early_submovement_scores.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])
    late_submovement_agg = late_submovement_scores.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])

    mean_early_submovement, sem_early_submovement = get_mean_sem(early_submovement_agg, ordered_columns)
    mean_late_submovement, sem_late_submovement = get_mean_sem(late_submovement_agg, ordered_columns)

    early_submovement_y = list(range(len(mean_early_submovement)))
    late_submovement_y = list(range(len(mean_late_submovement)))

    matplotlib.rcParams['font.family'] = "sans-serif"
    matplotlib.rcParams['font.sans-serif'] = "Arial"

    fig = plt.figure()
    fig.set_figwidth(7.48031)
    fig.set_dpi(1000)
    early_ax = plt.subplot2grid((1, 2), (0, 0))
    late_ax = plt.subplot2grid((1, 2), (0, 1))

    create_paired_bars(early_ax, early_submovement_y, mean_early_submovement, sem_early_submovement)
    create_paired_bars(late_ax, late_submovement_y, mean_late_submovement, sem_late_submovement)

    late_ax.legend(title=None, labels=["Control", "Dlx-CKO"])

    ctrl_y = [yval - bar_width / 2 for yval in early_submovement_y]
    ko_y = [yval + bar_width / 2 for yval in early_submovement_y]
    digits_close_y = early_submovement_y[2]
    digits_extend_y = ctrl_y[5]
    top_aim_y = ctrl_y[3]
    bottom_aim_y = ko_y[3]

    early_ax.plot([0.2, 0.5], [digits_extend_y, digits_extend_y], color="#005AB5", linewidth=1.0)
    early_ax.annotate('*',
                      xy=(sum([0.25, 0.5]) / 2, digits_extend_y-0.05),
                      xycoords='data',
                      ha='center',
                      color="#005AB5")

    early_ax.plot([0.18, 0.5], [digits_close_y, digits_close_y], color='black', linewidth=1.0)
    early_ax.annotate('*',
                      xy=(sum([0.18, 0.5]) / 2, digits_close_y - 0.05),
                      xycoords='data',
                      ha='center')

    early_ax.plot([0.1, 0.1], [bottom_aim_y, top_aim_y], color='black', linewidth=1.0)
    late_ax.plot([0.1, 0.1], [bottom_aim_y, top_aim_y], color='black', linewidth=1.0)
    early_ax.annotate('*',
                      xy=(0.12, early_submovement_y[3]+0.25),
                      xycoords='data',
                      ha='center')
    late_ax.annotate('*',
                      xy=(0.12, early_submovement_y[3]+0.25),
                      xycoords='data',
                      ha='center')

    early_ax.set_title('early training')
    late_ax.set_title('late training')

    early_ax.set_yticks(early_submovement_y)
    early_ax.set_yticklabels([column.label for column in ordered_columns])
    late_ax.tick_params(left=False, labelleft=False)

    plt.tight_layout(pad=0.2)
    plt.savefig('/Users/Krista/Desktop/semiQuant/submovements_20220209_small_ylim.pdf')
    plt.close('all')
