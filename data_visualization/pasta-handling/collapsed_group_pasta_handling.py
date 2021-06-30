import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path



save_dir = '/Users/Krista/OneDrive - Umich/pasta_handling'

palette = {"Control": 'b', "Knock-Out": 'r'}

# experiment = database_pkg.Models.experiments.Experiment.get_by_name("pasta-handling")

ph_summary_data = list()
ph_summary_data_long = list()
# for ph_summary in experiment.scored_pasta_handling:
#     session = database_pkg.Models.sessions.Session.query.get(ph_summary.session_id)
#     mouse = database_pkg.Models.mice.Mouse.query.get(session.mouse_id)
#
#     if mouse.genotype:
#         genotype = 'Knock-Out'
#     else:
#         genotype = 'Control'
#
#     new_row = {'eartag': mouse.eartag,
#                'genotype': genotype,
#                'birthdate': mouse.birthdate,
#                'sex': mouse.sex,
#                'session_date': session.session_date,
#                'session_dir': session.session_dir,
#                'scored_session_dir': ph_summary.scored_session_dir,
#                'trial_num': ph_summary.trial_num,
#                }
#     trial_details = {'time_to_eat': ph_summary.time_to_eat,
#                      'grasp_paw_start': ph_summary.grasp_paw_start,
#                      'guide_paw_start': ph_summary.guide_paw_start,
#                      'left_forepaw_adjustments': ph_summary.left_forepaw_adjustments,
#                      'right_forepaw_adjustments': ph_summary.right_forepaw_adjustments,
#                      'left_forepaw_failure_to_contact': ph_summary.left_forepaw_failure_to_contact,
#                      'right_forepaw_failure_to_contact': ph_summary.right_forepaw_failure_to_contact,
#                      'guid_grasp_switch': ph_summary.guide_grasp_switch,
#                      'drops': ph_summary.drops,
#                      'mouth_pulling': ph_summary.mouth_pulling,
#                      'pasta_long_paws_together': ph_summary.pasta_long_paws_together,
#                      'pasta_short_paws_apart': ph_summary.pasta_short_paws_apart,
#                      'abnormal_posture': ph_summary.abnormal_posture,
#                      'iron_grip': ph_summary.iron_grip,
#                      'guide_around_grasp': ph_summary.guide_around_grasp,
#                      'angling_with_head_tilt': ph_summary.angling_with_head_tilt
#                      }
#     ph_summary_data_long.append(dict(**new_row, **trial_details))
#
#     for key in trial_details.keys():
#         this_row = dict(**new_row,
#                         **{'trial measure': key,
#                            'value': trial_details[key]})
#         ph_summary_data.append(this_row)

ph_summary_df = pd.DataFrame.from_records(ph_summary_data)
ph_summary_df.to_csv('/Users/Krista/OneDrive - Umich/figures/all_scored_pasta_handling_20210131.csv')
ph_summary_long_df = pd.DataFrame.from_records(ph_summary_data_long)

sns.set_theme(context='paper', style="white")
figure, axis = plt.subplots(2, 1)

# sns.catplot(ax=axis[0],
#             data=ph_summary_df[ph_summary_df["trial measure"].isin(["time_to_eat"])],
#             kind='bar',
#             x="trial measure",
#             y="value",
#             hue='genotype',
#             palette=palette,
#             legend=False)
# axis[0][0].set_xticklabels(["Time to Eat"])
# axis[0][0].set(xlabel='', ylabel="Time (minutes)")
# axis[0][0].set_title(f'Time to Eat Pasta by Genotype')
# plt.legend(title='Genotype')

# sns.catplot(axis[1][0],
#                  data=ph_summary_df[ph_summary_df["trial measure"].isin(["left_forepaw_adjustments", "right_forepaw_adjustments"])],
#                 kind='bar',
#                 x="trial measure",
#                 y="value",
#                 hue='genotype',
#                 palette=palette,
#                 legend=False)
# axis[1][0].set_xticklabels(["Right", "Left"])
# axis[1][0].set(xlabel='', ylabel="Number of Adjustments")
# axis[1][0].set_title(f'Number of Forepaw Adjustments by Genotype')
# plt.tight_layout()
# plt.show()
# plt.savefig(str(Path(save_dir).joinpath('time_to_eat.jpeg')), bbox_inches='tight')
# plt.close()

#############

# g1 = sns.catplot(data=ph_summary_df[ph_summary_df["trial measure"].isin(["left_forepaw_adjustments", "right_forepaw_adjustments"])],
#                 kind='bar',
#                 x="trial measure",
#                 y="value",
#                 hue='genotype',
#                 palette=palette,
#                 legend=False)
# g1.ax.set_xticklabels(["Right", "Left"])
# g1.ax.set(xlabel='', ylabel="Number of Adjustments")
# g1.ax.set_title(f'Number of Forepaw Adjustments by Genotype')
# plt.legend(title='Genotype')
# plt.savefig(str(Path(save_dir).joinpath('num_forepaw_adjustments.jpeg')), bbox_inches='tight')
# plt.close()

#############
df_atypical_binary = ph_summary_df[ph_summary_df["trial measure"].isin(["pasta_long_paws_together",
                                                                        "pasta_short_paws_apart"])]
df_atypical_binary.value[df_atypical_binary.value == 'True'] = 1
df_atypical_binary.value[df_atypical_binary.value == 'False'] = 0
df_atypical_binary["value"] = df_atypical_binary.loc[:, "value"].astype(bool)

# sns.catplot(data=df_atypical_binary,
#             kind='bar',
#             x="trial measure",
#             y="value",
#             hue='genotype',
#             palette=palette,
#             legend=False,
#             ax=axis[1])
#
# axis[1].set_title("")
# axis[1].set_xlabel("")
# axis[1].set_ylabel("Percent of Sessions")
# axis[1].set_xticklabels(["Pasta Long,\nPaws Together",
#                          "Pasta Short,\nPaws Apart"])
# plt.legend(title='Genotype')

#############
df_atypical_counts = ph_summary_df[ph_summary_df["trial measure"].isin(["left_forepaw_failure_to_contact",
                                                                        "right_forepaw_failure_to_contact",
                                                                        "guid_grasp_switch",
                                                                        "drops",
                                                                        "mouth_pulling"])]
cat_plot_col_dict = {"left_forepaw_failure_to_contact": 'left',
                     "right_forepaw_failure_to_contact": 'left',
                     "guid_grasp_switch": 'left',
                     "drops": 'left',
                     "mouth_pulling": 'left',
                     "pasta_long_paws_together": 'right',
                     "pasta_short_paws_apart": 'right'
                     }

df_atypical_counts["value"] = df_atypical_counts.loc[:, "value"].astype(float)
df_atypical_binary = ph_summary_df[ph_summary_df["trial measure"].isin(["pasta_long_paws_together",
                                                                        "pasta_short_paws_apart"])]
df_atypical_binary.value[df_atypical_binary.value == 'True'] = 1
df_atypical_binary.value[df_atypical_binary.value == 'False'] = 0
df_atypical_binary["value"] = df_atypical_binary.loc[:, "value"].astype(bool)

all_atypical = pd.concat([df_atypical_binary, df_atypical_counts])

all_atypical['cat_plot_col'] = all_atypical.apply(lambda x: cat_plot_col_dict[x['trial measure']], axis=1)

f = sns.catplot(data=all_atypical,
                kind='bar',
                x="trial measure",
                y="value",
                hue='genotype',
                palette=palette,
                legend=False,
                col='cat_plot_col',
                hue_order=['Control', 'Knock-Out'],
                col_order=['left', 'right'],
                sharex=False,
                sharey=False)

f.axes[0][0].set_title("")
f.axes[0][0].set_xlabel("")
f.axes[0][0].set_ylabel("mean observations / session")
f.axes[0][0].set_xticklabels(["left paw\nno contact",
                              "right paw\nno contact",
                              "guide/grasp\nswitch",
                              "drops",
                              "mouth\npulling"])
f.axes[0][0].set_yticks([0, 1, 2])
f.axes[0][0].set_yticklabels(['0', '1', '2'])

f.axes[0][1].set_title("")
f.axes[0][1].set_xlabel("")
f.axes[0][1].set_ylabel("percent of sessions")
f.axes[0][1].set_xticklabels(["pasta long,\npaws together",
                              "pasta short,\npaws apart"])
f.axes[0][1].set_yticks([0, 0.4, 0.8])
f.axes[0][1].set_yticklabels(['0', '40', '80'])

plt.legend(title='Genotype')
# g3.fig.suptitle("Atypical Handling Patterns by Genotype")
plt.tight_layout()
plt.savefig(str(Path(save_dir).joinpath('atypical_handling_patterns.pdf')))

#############

# g4 = sns.catplot(data=ph_summary_df[ph_summary_df["trial measure"].isin(["grasp_paw_start",
#                                                                          "guide_paw_start"])],
#                  kind='count',
#                  x="value",
#                  y=None,
#                  hue='genotype',
#                  col="trial measure",
#                  palette=palette,
#                  legend=False,
#                  aspect=11.7/8.27
#                  )
# axes = g4.axes.flatten()
# axes[0].set_title("")
# axes[0].set_xlabel("Grasp Paw")
# axes[0].set_ylabel("Session Count")
# axes[0].set_xticklabels(["Left", "Right"])
#
# axes[1].set_title("")
# axes[1].set_xlabel("Guide Paw")
# axes[1].set_xticklabels(["Left", "Right"])
#
# plt.legend(title='Genotype')
# g4.fig.suptitle("Grasp and Guide Paw Preference at Session Start by Genotype")
# plt.savefig(str(Path(save_dir).joinpath('guide_grasp_paw_pref.jpeg')), bbox_inches='tight')
# plt.close()

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
