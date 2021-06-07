import pandas as pd
import numpy as np
import matplotlib
from scipy import stats
import matplotlib.pyplot as plt

from database_pkg import Mouse, Experiment, Session

palette = {"Control": 'b', "Knock-Out": 'r'}

experiment = Experiment.get_by_name("dlxCKO-pasta-handling")

ph_summary_data = list()
ph_summary_data_long = list()
for ph_summary in experiment.scored_pasta_handling:
    session = Session.query.get(ph_summary.session_id)
    mouse = Mouse.query.get(session.mouse_id)

    if mouse.genotype == 'Dlx-CKO':
        genotype = 'Knock-Out'
    elif mouse.genotype == 'Dlx-CKO Control':
        genotype = 'Control'
    else:
        breakpoint()

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
                     'guide_grasp_switch': ph_summary.guide_grasp_switch,
                     'drops': ph_summary.drops,
                     'mouth_pulling': ph_summary.mouth_pulling,
                     'pasta_long_paws_together': ph_summary.pasta_long_paws_together,
                     'pasta_short_paws_apart': ph_summary.pasta_short_paws_apart,
                     'abnormal_posture': ph_summary.abnormal_posture,
                     'iron_grip': ph_summary.iron_grip,
                     'guide_around_grasp': ph_summary.guide_around_grasp,
                     'angling_with_head_tilt': ph_summary.angling_with_head_tilt,
                     'left_forepaw_failure_to_contact_bool': ph_summary.left_forepaw_failure_to_contact_bool,
                     'right_forepaw_failure_to_contact_bool': ph_summary.right_forepaw_failure_to_contact_bool,
                     'guide_grasp_switch_bool': ph_summary.guide_grasp_switch_bool,
                     'drops_bool': ph_summary.drops_bool,
                     'mouth_pulling_bool': ph_summary.mouth_pulling_bool,
                     'pasta_long_paws_together_bool': ph_summary.pasta_long_paws_together_bool,
                     'pasta_short_paws_apart_bool': ph_summary.pasta_short_paws_apart_bool,
                     'abnormal_posture_bool': ph_summary.abnormal_posture_bool,
                     'iron_grip_bool': ph_summary.iron_grip_bool,
                     'guide_around_grasp_bool': ph_summary.guide_around_grasp_bool,
                     'angling_with_head_tilt_bool': ph_summary.angling_with_head_tilt_bool
                     }
    ph_summary_data_long.append(dict(**new_row, **trial_details))

    for key in trial_details.keys():
        this_row = dict(**new_row,
                        **{'trial measure': key,
                           'value': trial_details[key]})
        ph_summary_data.append(this_row)

ph_summary_df = pd.DataFrame.from_records(ph_summary_data)
ph_summary_long_df = pd.DataFrame.from_records(ph_summary_data_long)

## statistics
control_trials = ph_summary_long_df[ph_summary_long_df.genotype == 'Control'].groupby('session_dir').agg(np.sum)
knockout_trials = ph_summary_long_df[ph_summary_long_df.genotype == 'Knock-Out'].groupby('session_dir').agg(np.sum)
stats.ttest_ind(control_trials["left_forepaw_adjustments"], knockout_trials["left_forepaw_adjustments"],
                equal_var=False)
stats.ttest_ind(control_trials["right_forepaw_adjustments"], knockout_trials["right_forepaw_adjustments"],
                equal_var=False)
stats.ttest_ind(control_trials["left_forepaw_failure_to_contact"], knockout_trials["left_forepaw_failure_to_contact"],
                equal_var=False)
stats.ttest_ind(control_trials["right_forepaw_failure_to_contact"], knockout_trials["right_forepaw_failure_to_contact"],
                equal_var=False)
stats.ttest_ind(control_trials["guide_grasp_switch"], knockout_trials["guide_grasp_switch"], equal_var=False)
stats.ttest_ind(control_trials["drops"], knockout_trials["drops"])
stats.ttest_ind(control_trials["mouth_pulling"], knockout_trials["mouth_pulling"])
stats.ttest_ind(control_trials["mouth_pulling"], knockout_trials["mouth_pulling"], equal_var=False)
stats.ttest_ind(control_trials["pasta_long_paws_together"], knockout_trials["pasta_long_paws_together"])
stats.ttest_ind(control_trials["pasta_short_paws_apart"], knockout_trials["pasta_short_paws_apart"])

out_df = ph_summary_long_df.groupby("genotype").agg([np.mean, stats.sem])
out_df = out_df.transpose().reset_index()
out = out_df.rename(
    columns={"level_0": 'measure', 'level_1': "statistic", 'Control': "control", 'Knock-Out': 'knockout'})

desired_measures = ['left_forepaw_adjustments',
                    'right_forepaw_adjustments',
                    'left_forepaw_failure_to_contact',
                    'right_forepaw_failure_to_contact',
                    'guide_grasp_switch',
                    'drops',
                    'mouth_pulling',
                    'pasta_long_paws_together',
                    'pasta_short_paws_apart']
# ,
#                     'abnormal_posture',
#                     'iron_grip',
#                     'guide_around_grasp',
#                     'angling_with_head_tilt'

out_dict = {'left_forepaw_adjustments': {'ctrl_mean': None, 'ctrl_sem': None, 'ko_mean': None, 'ko_sem': None},
            'right_forepaw_adjustments': {'ctrl_mean': None, 'ctrl_sem': None, 'ko_mean': None, 'ko_sem': None},
            'left_forepaw_failure_to_contact': {'ctrl_mean': None, 'ctrl_sem': None, 'ko_mean': None, 'ko_sem': None},
            'right_forepaw_failure_to_contact': {'ctrl_mean': None, 'ctrl_sem': None, 'ko_mean': None, 'ko_sem': None},
            'guide_grasp_switch': {'ctrl_mean': None, 'ctrl_sem': None, 'ko_mean': None, 'ko_sem': None},
            'drops': {'ctrl_mean': None, 'ctrl_sem': None, 'ko_mean': None, 'ko_sem': None},
            'mouth_pulling': {'ctrl_mean': None, 'ctrl_sem': None, 'ko_mean': None, 'ko_sem': None},
            'pasta_long_paws_together': {'ctrl_mean': None, 'ctrl_sem': None, 'ko_mean': None, 'ko_sem': None},
            'pasta_short_paws_apart': {'ctrl_mean': None, 'ctrl_sem': None, 'ko_mean': None, 'ko_sem': None}}
for index, row in out.iterrows():
    if index == 0 or row.measure not in desired_measures:
        continue

    if row.statistic == 'mean':
        out_dict[row.measure]['ctrl_mean'] = row.control
        out_dict[row.measure]['ko_mean'] = row.knockout
    elif row.statistic == 'sem':
        out_dict[row.measure]['ctrl_sem'] = row.control
        out_dict[row.measure]['ko_sem'] = row.knockout

out_df = pd.DataFrame.from_records(out_dict)
plot_df = out_df.transpose()

atypical_behavior_order = ["left_forepaw_failure_to_contact",
                           "right_forepaw_failure_to_contact",
                           "pasta_long_paws_together",
                           "pasta_short_paws_apart",
                           "guide_grasp_switch",
                           "mouth_pulling",
                           "drops"]
mapping = {atypical_behavior: i for i, atypical_behavior in enumerate(atypical_behavior_order)}

key = plot_df.index.map(mapping)
plot_df = plot_df.iloc[key.argsort()]
plot_df = plot_df.rename_axis('measure').reset_index()
plot_df = plot_df[plot_df['measure'].isin(atypical_behavior_order)]

fig, ax = plt.subplots()
fig.set_figwidth(7.48031)
fig.set_figheight(2.5)
fig.set_dpi(1000)
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"

ax1 = plt.subplot2grid((1, 1), (0, 0))

plot_df.plot.bar(x='measure', y=["ctrl_mean", "ko_mean"],
                 ax=ax1,
                 color={"ctrl_mean": 'b', "ko_mean": 'r'},
                 yerr=[plot_df["ctrl_sem"], plot_df["ko_sem"]],
                 capsize=2)
ax1.set_xticklabels(["left forepaw\nno contact",
                     "right forepaw\nno contact",
                     "pasta long,\npaws together",
                     "pasta short,\npaws apart",
                     "guide/grasp\nswitch",
                     "mouth pulling",
                     "drops"],
                    rotation='horizontal')
ax1.set_xlabel(None)
ax1.set_ylabel('mean observations / trial')
ax1.set_yticks([0, 0.5, 1, 1.5])
ax1.set_yticklabels([0, 0.5, 1, 1.5])
ax1.legend(title=None, labels=["control", "Dlx-CKO"])
plt.tight_layout()
plt.savefig('/Users/Krista/OneDrive - Umich/figures/figures_ai/figure2/fig2_20210506.pdf')
