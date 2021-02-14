import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

import database_pkg.Models.experiments
import database_pkg.Models.super_classes

save_dir = '/Users/Krista/OneDrive - Umich/pasta_handling'

palette = {"Control": 'b', "Knock-Out": 'r'}

experiment = database_pkg.Models.experiments.Experiment.get_by_name("pasta-handling")

ph_summary_data = list()
ph_summary_data_long = list()
for ph_summary in experiment.scored_pasta_handling:
    session = database_pkg.Models.sessions.Session.query.get(ph_summary.session_id)
    mouse = database_pkg.Models.mice.Mouse.query.get(session.mouse_id)

    if mouse.genotype:
        genotype = 'Knock-Out'
    else:
        genotype = 'Control'

    new_row = {'eartag': mouse.eartag,
               'genotype': genotype,
               'birthdate': mouse.birthdate,
               'sex': mouse.sex,
               'session_date': session.session_date,
               'session_dir': session.session_dir,
               'scored_session_dir': ph_summary.scored_session_dir,
               'trial_num': ph_summary.trial_num,
               }
    trial_details = {'time_to_eat': ph_summary.time_to_eat,
                     'grasp_paw_start': ph_summary.grasp_paw_start,
                     'guide_paw_start': ph_summary.guide_paw_start,
                     'left_forepaw_adjustments': ph_summary.left_forepaw_adjustments,
                     'right_forepaw_adjustments': ph_summary.right_forepaw_adjustments,
                     'left_forepaw_failure_to_contact': ph_summary.left_forepaw_failure_to_contact,
                     'right_forepaw_failure_to_contact': ph_summary.right_forepaw_failure_to_contact,
                     'guid_grasp_switch': ph_summary.guide_grasp_switch,
                     'drops': ph_summary.drops,
                     'mouth_pulling': ph_summary.mouth_pulling,
                     'pasta_long_paws_together': ph_summary.pasta_long_paws_together,
                     'pasta_short_paws_apart': ph_summary.pasta_short_paws_apart,
                     'abnormal_posture': ph_summary.abnormal_posture,
                     'iron_grip': ph_summary.iron_grip,
                     'guide_around_grasp': ph_summary.guide_around_grasp,
                     'angling_with_head_tilt': ph_summary.angling_with_head_tilt
                     }
    ph_summary_data_long.append(dict(**new_row, **trial_details))

    for key in trial_details.keys():
        this_row = dict(**new_row,
                        **{'trial measure': key,
                           'value': trial_details[key]})
        ph_summary_data.append(this_row)

ph_summary_df = pd.DataFrame.from_records(ph_summary_data)
ph_summary_df.to_csv('/Users/Krista/OneDrive - Umich/all_scored_pasta_handling_20210131.csv')
ph_summary_long_df = pd.DataFrame.from_records(ph_summary_data_long)

g = sns.catplot(data=ph_summary_df[ph_summary_df["trial measure"].isin(["time_to_eat"])],
                kind='bar',
                x="trial measure",
                y="value",
                hue='genotype',
                palette=palette,
                legend=False)
g.ax.set_xticklabels(["Time to Eat"])
g.ax.set(xlabel='', ylabel="Time (minutes)")
g.ax.set_title(f'Time to Eat Pasta by Genotype')
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('time_to_eat.jpeg')), bbox_inches='tight')
plt.close()

#############

g1 = sns.catplot(data=ph_summary_df[ph_summary_df["trial measure"].isin(["left_forepaw_adjustments", "right_forepaw_adjustments"])],
                kind='bar',
                x="trial measure",
                y="value",
                hue='genotype',
                palette=palette,
                legend=False)
g1.ax.set_xticklabels(["Right", "Left"])
g1.ax.set(xlabel='', ylabel="Number of Adjustments")
g1.ax.set_title(f'Number of Forepaw Adjustments by Genotype')
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('num_forepaw_adjustments.jpeg')), bbox_inches='tight')
plt.close()

#############

g2 = sns.catplot(data=ph_summary_df[ph_summary_df["trial measure"].isin(["pasta_long_paws_together",
                                                                         "pasta_short_paws_apart",
                                                                         "iron_grip",
                                                                         "guide_around_grasp"])],
                 kind='bar',
                 x="trial measure",
                 y="value",
                 hue='genotype',
                 palette=palette,
                 legend=False,
                 aspect=11.7/8.27)

axes = g2.axes.flatten()
axes[0].set_title("")
axes[0].set_xlabel("")
axes[0].set_ylabel("Percent of Sessions")
axes[0].set_xticklabels(["Pasta Long,\nPaws Together",
                         "Pasta Short,\nPaws Apart",
                         "Iron Grip",
                         "Guide\nAround Grasp"])
axes[0].set_yticklabels([0, 10, 20, 30, 40, 50, 60, 70, 80])
plt.legend(title='Genotype')
g2.fig.suptitle("Atypical Handling Patterns by Genotype")
plt.savefig(str(Path(save_dir).joinpath('atypical_handling_patterns_boolean.jpeg')), bbox_inches='tight')
plt.close()

#############

g3 = sns.catplot(data=ph_summary_df[ph_summary_df["trial measure"].isin(["left_forepaw_failure_to_contact",
                                                                         "right_forepaw_failure_to_contact",
                                                                         "guid_grasp_switch",
                                                                         "drops",
                                                                         "mouth_pulling"])],
                 kind='bar',
                 x="trial measure",
                 y="value",
                 hue='genotype',
                 palette=palette,
                 legend=False,
                 aspect=11.7/8.27)

axes = g3.axes.flatten()
axes[0].set_title("")
axes[0].set_xlabel("")
axes[0].set_ylabel("Observations / Session")
axes[0].set_xticklabels(["Left Paw\nNo Contact",
                         "Right Paw\nNo Contact",
                         "Guide/Grasp\nSwitch",
                         "Drops",
                         "Mouth\nPulling"])

plt.legend(title='Genotype')
g3.fig.suptitle("Atypical Handling Patterns by Genotype")
plt.savefig(str(Path(save_dir).joinpath('atypical_handling_patterns.jpeg')), bbox_inches='tight')
plt.close()

#############

g4 = sns.catplot(data=ph_summary_df[ph_summary_df["trial measure"].isin(["grasp_paw_start",
                                                                         "guide_paw_start"])],
                 kind='count',
                 x="value",
                 y=None,
                 hue='genotype',
                 col="trial measure",
                 palette=palette,
                 legend=False,
                 aspect=11.7/8.27
                 )
axes = g4.axes.flatten()
axes[0].set_title("")
axes[0].set_xlabel("Grasp Paw")
axes[0].set_ylabel("Session Count")
axes[0].set_xticklabels(["Left", "Right"])

axes[1].set_title("")
axes[1].set_xlabel("Guide Paw")
axes[1].set_xticklabels(["Left", "Right"])

plt.legend(title='Genotype')
g4.fig.suptitle("Grasp and Guide Paw Preference at Session Start by Genotype")
plt.savefig(str(Path(save_dir).joinpath('guide_grasp_paw_pref.jpeg')), bbox_inches='tight')
plt.close()

#############
#
# g3 = sns.catplot(data=ph_summary_df[ph_summary_df["trial measure"].isin(["guide_paw_start",
#                                                                          "grasp_paw_start"])],
#                  kind='count',
#                  x=None,
#                  y='value',
#                  hue='genotype',
#                  palette=palette,
#                  legend=False,
#                  aspect=11.7/8.27
#                  )
# g3.ax.set_xticklabels(["Guide Paw", "Grasp Paw"])
# g3.ax.set(xlabel='', ylabel="Number of Sessions Starting With")
# g3.ax.set_title(f'Guide and Grasp Paw Preference by Genotype')
# plt.legend(title='Genotype')
# plt.savefig(str(Path(save_dir).joinpath('guide_grasp_paw_pref.jpeg')), bbox_inches='tight')
# plt.close()


