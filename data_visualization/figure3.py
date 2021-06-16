from database_pkg import Experiment, GroomingTrial, Mouse
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib

exp = Experiment.get_by_name('dlxCKO-grooming')

data_by_bout = list()

for session in exp.sessions:

    mouse = Mouse.query.get(session.mouse_id)

    total_time_grooming = 0
    num_bouts = 0
    for groom_sum in GroomingTrial.query.filter_by(session_id=session.session_id).all():
        total_time_grooming += groom_sum.total_time_grooming
        num_bouts += groom_sum.num_bouts

        for bout in groom_sum.bouts:
            data_by_bout.append({'bout_id': bout.grooming_bout_id,
                                 'session_id': session.session_id,
                                 'genotype': mouse.genotype,
                                 'bout_time': (bout.bout_end - bout.bout_start) / 100,
                                 'total_transitions': bout.total_num_transitions,
                                 'total_incorrect_transitions': bout.num_incorrect_transitions,
                                 'num_initiation_incorrect_transitions': sum(
                                    bout.initiation_incorrect_transitions.values()),
                                 'num_skipped_transitions': sum(
                                    bout.skipped_transitions.values()),
                                 'num_reversed_transitions': sum(
                                    bout.reversed_transitions.values()),
                                 'num_aborted_transitions': sum(
                                    bout.aborted_transitions.values())
                                 })

by_bout_df = pd.DataFrame.from_records(data_by_bout)

prop_by_bout_df = by_bout_df
prop_by_bout_df['prop_initiation_incorrect_transitions'] = by_bout_df['num_initiation_incorrect_transitions'] / \
                                                            by_bout_df['total_incorrect_transitions']
prop_by_bout_df['prop_skipped_transitions'] = by_bout_df['num_skipped_transitions'] / \
                                                            by_bout_df['total_incorrect_transitions']
prop_by_bout_df['prop_reversed_transitions'] = by_bout_df['num_reversed_transitions'] / \
                                                            by_bout_df['total_incorrect_transitions']
prop_by_bout_df['prop_aborted_transitions'] = by_bout_df['num_aborted_transitions'] / \
                                                            by_bout_df['total_incorrect_transitions']

agg_by_bout = prop_by_bout_df.groupby("genotype").agg([np.mean, stats.sem])
agg_by_bout_tp = agg_by_bout.transpose().reset_index()
agg_by_bout_plot = agg_by_bout_tp.rename(
    columns={"level_0": 'measure', 'level_1': 'statistic', 'Dlx-CKO Control': 'control', 'Dlx-CKO': 'knockout'})

bout_mean_plot_dict = {'bout_time': {'ctrl_mean': None, 'ko_mean': None},
                       'total_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'total_incorrect_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'prop_initiation_incorrect_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'prop_skipped_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'prop_reversed_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'prop_aborted_transitions': {'ctrl_mean': None, 'ko_mean': None}}
bout_sem_plot_dict = {'bout_time': {'ctrl_sem': None, 'ko_sem': None},
                      'total_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'total_incorrect_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'prop_initiation_incorrect_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'prop_skipped_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'prop_reversed_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'prop_aborted_transitions': {'ctrl_sem': None, 'ko_sem': None}}
for index, row in agg_by_bout_plot.iterrows():
    if row.measure not in bout_mean_plot_dict.keys():
        continue
    if row.statistic == 'mean':
        bout_mean_plot_dict[row.measure]['ctrl_mean'] = row.control
        bout_mean_plot_dict[row.measure]['ko_mean'] = row.knockout
    elif row.statistic == 'sem':
        bout_sem_plot_dict[row.measure]['ctrl_sem'] = row.control
        bout_sem_plot_dict[row.measure]['ko_sem'] = row.knockout

bout_mean_plot_df = pd.DataFrame.from_records(bout_mean_plot_dict).transpose().reset_index()
bout_mean_plot_df.rename(columns={'index': 'measure'}, inplace=True)
bout_sem_plot_df = pd.DataFrame.from_records(bout_sem_plot_dict).transpose().reset_index()
bout_sem_plot_df.rename(columns={'index': 'measure'}, inplace=True)

mean_time_grooming_bout = bout_mean_plot_df[bout_mean_plot_df.measure == "bout_time"]
sem_time_grooming_bout = bout_sem_plot_df[bout_sem_plot_df.measure == "bout_time"]

mean_total_incorrect_transitions_bout = bout_mean_plot_df[bout_mean_plot_df.measure == "total_incorrect_transitions"]
sem_total_incorrect_transitions_bout = bout_sem_plot_df[bout_sem_plot_df.measure == "total_incorrect_transitions"]

mean_total_transitions_bout = bout_mean_plot_df[bout_mean_plot_df.measure == "total_transitions"]
sem_total_transitions_bout = bout_sem_plot_df[bout_sem_plot_df.measure == "total_transitions"]

mean_incorrect_transitions_prop_bout = bout_mean_plot_df[bout_mean_plot_df.measure.isin(["prop_initiation_incorrect_transitions",
                                                                                       "prop_skipped_transitions",
                                                                                       "prop_reversed_transitions",
                                                                                       "prop_aborted_transitions"])]
sem_incorrect_transitions_prop_bout = bout_sem_plot_df[bout_sem_plot_df.measure.isin(["prop_initiation_incorrect_transitions",
                                                                                       "prop_skipped_transitions",
                                                                                       "prop_reversed_transitions",
                                                                                       "prop_aborted_transitions"])]
##

num_bouts_per_session = by_bout_df.groupby(["session_id", 'genotype']).count()
agg_num_bouts_per_session = num_bouts_per_session.groupby("genotype").agg([np.mean, stats.sem])
agg_num_bouts_tp = agg_num_bouts_per_session.transpose().reset_index()
agg_num_bouts_plot = agg_num_bouts_tp.rename(columns={'level_0': 'measure', 'level_1': 'statistic', 'Dlx-CKO': 'knockout', 'Dlx-CKO Control': 'control'})

mean_num_bouts_dict = {'bout_id': {'ctrl_mean': None, 'ko_mean': None}}
sem_num_bouts_dict = {'bout_id': {'ctrl_sem': None, 'ko_sem': None}}

for index, row in agg_num_bouts_plot.iterrows():
    if row.measure not in mean_num_bouts_dict.keys():
        continue
    if row.statistic == 'mean':
        mean_num_bouts_dict[row.measure]['ctrl_mean'] = row.control
        mean_num_bouts_dict[row.measure]['ko_mean'] = row.knockout
    elif row.statistic == 'sem':
        sem_num_bouts_dict[row.measure]['ctrl_sem'] = row.control
        sem_num_bouts_dict[row.measure]['ko_sem'] = row.knockout

mean_num_bouts_plot_df = pd.DataFrame.from_records(mean_num_bouts_dict).transpose().reset_index()
mean_num_bouts_plot_df.rename(columns={'index': 'measure'}, inplace=True)
sem_num_bouts_plot_df = pd.DataFrame.from_records(sem_num_bouts_dict).transpose().reset_index()
sem_num_bouts_plot_df.rename(columns={'index': 'measure'}, inplace=True)

agg_by_session = by_bout_df.groupby(["session_id", 'genotype']).agg(np.sum).reset_index()
agg_by_session['prop_initiation_incorrect_transitions'] = agg_by_session['num_initiation_incorrect_transitions'] / \
                                                          agg_by_session['total_incorrect_transitions']
agg_by_session['prop_skipped_transitions'] = agg_by_session['num_skipped_transitions'] / \
                                                          agg_by_session['total_incorrect_transitions']
agg_by_session['prop_reversed_transitions'] = agg_by_session['num_reversed_transitions'] / \
                                                          agg_by_session['total_incorrect_transitions']
agg_by_session['prop_aborted_transitions'] = agg_by_session['num_aborted_transitions'] / \
                                                          agg_by_session['total_incorrect_transitions']

# statistics (transitions)

utest_initiation_incorrect = stats.mannwhitneyu(
    x=agg_by_session[agg_by_session['genotype'] == 'Dlx-CKO Control']['prop_initiation_incorrect_transitions'],
    y=agg_by_session[agg_by_session['genotype'] == 'Dlx-CKO']['prop_initiation_incorrect_transitions'], alternative='two-sided')
utest_skipped = stats.mannwhitneyu(
    x=agg_by_session[agg_by_session['genotype'] == 'Dlx-CKO Control']['prop_skipped_transitions'],
    y=agg_by_session[agg_by_session['genotype'] == 'Dlx-CKO']['prop_skipped_transitions'], alternative='two-sided')
utest_reversed = stats.mannwhitneyu(
    x=agg_by_session[agg_by_session['genotype'] == 'Dlx-CKO Control']['prop_reversed_transitions'],
    y=agg_by_session[agg_by_session['genotype'] == 'Dlx-CKO']['prop_reversed_transitions'], alternative='two-sided')
utest_aborted = stats.mannwhitneyu(
    x=agg_by_session[agg_by_session['genotype'] == 'Dlx-CKO Control']['prop_aborted_transitions'],
    y=agg_by_session[agg_by_session['genotype'] == 'Dlx-CKO']['prop_aborted_transitions'], alternative='two-sided')
ttest_total_transitions = stats.ttest_ind(
    by_bout_df[by_bout_df['genotype'] == 'Dlx-CKO Control']['total_transitions'],
    by_bout_df[by_bout_df['genotype'] == 'Dlx-CKO']['total_transitions'])
ttest_incorrect_transitions = stats.ttest_ind(
    by_bout_df[by_bout_df['genotype'] == 'Dlx-CKO Control']['total_incorrect_transitions'],
    by_bout_df[by_bout_df['genotype'] == 'Dlx-CKO']['total_incorrect_transitions'], equal_var=False) # var_ctl=0.675, var_ko=0.595

agg_by_session = agg_by_session.groupby("genotype").agg([np.mean, stats.sem])
agg_by_session_tp = agg_by_session.transpose().reset_index()
agg_by_session_plot = agg_by_session_tp.rename(
    columns={"level_0": 'measure', 'level_1': "statistic", 'Dlx-CKO Control': "control", 'Dlx-CKO': 'knockout'})

session_mean_plot_dict = {'bout_time': {'ctrl_mean': None, 'ko_mean': None},
                       'total_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'total_incorrect_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'prop_initiation_incorrect_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'prop_skipped_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'prop_reversed_transitions': {'ctrl_mean': None, 'ko_mean': None},
                       'prop_aborted_transitions': {'ctrl_mean': None, 'ko_mean': None}}
session_sem_plot_dict = {'bout_time': {'ctrl_sem': None, 'ko_sem': None},
                      'total_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'total_incorrect_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'prop_initiation_incorrect_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'prop_skipped_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'prop_reversed_transitions': {'ctrl_sem': None, 'ko_sem': None},
                      'prop_aborted_transitions': {'ctrl_sem': None, 'ko_sem': None}}

for index, row in agg_by_session_plot.iterrows():
    if row.measure not in session_mean_plot_dict.keys():
        continue
    if row.statistic == 'mean':
        session_mean_plot_dict[row.measure]['ctrl_mean'] = row.control
        session_mean_plot_dict[row.measure]['ko_mean'] = row.knockout
    elif row.statistic == 'sem':
        session_sem_plot_dict[row.measure]['ctrl_sem'] = row.control
        session_sem_plot_dict[row.measure]['ko_sem'] = row.knockout

session_mean_plot_df = pd.DataFrame.from_records(session_mean_plot_dict).transpose().reset_index()
session_mean_plot_df.rename(columns={'index': 'measure'}, inplace=True)
session_sem_plot_df = pd.DataFrame.from_records(session_sem_plot_dict).transpose().reset_index()
session_sem_plot_df.rename(columns={'index': 'measure'}, inplace=True)

mean_time_grooming_session = session_mean_plot_df[session_mean_plot_df.measure == "bout_time"]
sem_time_grooming_session = session_sem_plot_df[session_sem_plot_df.measure == "bout_time"]

# mean_total_incorrect_transitions_session = session_mean_plot_df[session_mean_plot_df.measure == "total_incorrect_transitions"]
# sem_total_incorrect_transitions_session = session_sem_plot_df[session_sem_plot_df.measure == "total_incorrect_transitions"]
#
# mean_total_transitions_session = session_mean_plot_df[session_mean_plot_df.measure == "total_transitions"]
# sem_total_transitions_session = session_sem_plot_df[session_sem_plot_df.measure == "total_transitions"]

mean_incorrect_transitions_prop_session = session_mean_plot_df[session_mean_plot_df.measure.isin(["prop_initiation_incorrect_transitions",
                                                                                       "prop_skipped_transitions",
                                                                                       "prop_reversed_transitions",
                                                                                       "prop_aborted_transitions"])]
sem_incorrect_transitions_prop_session = session_sem_plot_df[session_sem_plot_df.measure.isin(["prop_initiation_incorrect_transitions",
                                                                                       "prop_skipped_transitions",
                                                                                       "prop_reversed_transitions",
                                                                                       "prop_aborted_transitions"])]

mean_total_transitions_bout = bout_mean_plot_df[bout_mean_plot_df.measure.isin(["total_transitions",
                                                                                         "total_incorrect_transitions"])]
sem_total_transitions_bout = bout_sem_plot_df[bout_sem_plot_df.measure.isin(["total_transitions",
                                                                                      "total_incorrect_transitions"])]

# Plotting

fig, ax = plt.subplots()
w = 5.51181
fig.set_figwidth(w)
fig.set_dpi(1000)
cap_size = 4
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"

ax1 = plt.subplot2grid((2, 3), (0, 0))
ax2 = plt.subplot2grid((2, 3), (0, 1))
ax3 = plt.subplot2grid((2, 3), (0, 2))
ax4 = plt.subplot2grid((2, 3), (1, 1), colspan=2)
ax5 = plt.subplot2grid((2, 3), (1, 0))

mean_time_grooming_session.plot.bar(ax=ax1, y=['ctrl_mean', 'ko_mean'], color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                    yerr=[sem_time_grooming_session['ctrl_sem'], sem_time_grooming_session['ko_sem']],
                                    capsize=cap_size, legend=False)
ax1.set_ylim(0, 1000)
ax1.set_yticks([0, 420, 840])
ax1.set_yticklabels([0, 7, 14])
ax1.set_ylabel('mean time (m)')
ax1.set_xticklabels(['total grooming'], rotation='horizontal')

line_y = [mean_time_grooming_session['ko_mean'].item() + sem_time_grooming_session['ko_sem'].item() + 75]*2
line_x = [-0.125, 0.125]

ax1.plot(line_x, line_y, color='black', linewidth=1.0)
ax1.annotate('*', xy=(0, 835), xycoords='data', ha='center')


mean_num_bouts_plot_df.plot.bar(ax=ax2, y=['ctrl_mean', 'ko_mean'],
                                                  color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                                  yerr=[sem_num_bouts_plot_df['ctrl_sem'],
                                                        sem_num_bouts_plot_df['ko_sem']],
                                                  capsize=cap_size, legend=False)
ax2.set_ylim(0, 38)
ax2.set_yticks([0, 15, 30])
ax2.set_yticklabels([0, 15, 30])
ax2.set_ylabel('mean per session')
ax2.set_xticklabels(['number of bouts'], rotation='horizontal')

line_y = [mean_num_bouts_plot_df['ko_mean'].item() + sem_num_bouts_plot_df['ko_sem'].item() + 2]*2
line_x = [-0.125, 0.125]

ax2.plot(line_x, line_y, color='black', linewidth=1.0)
ax2.annotate('*',
             xy=(0, np.round(mean_num_bouts_plot_df['ko_mean'].item() + sem_num_bouts_plot_df['ko_sem'].item() + 2)),
             xycoords='data',
             ha='center')

mean_time_grooming_bout.plot.bar(ax=ax3, y=['ctrl_mean', 'ko_mean'], color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                    yerr=[sem_time_grooming_bout['ctrl_sem'], sem_time_grooming_bout['ko_sem']],
                                    capsize=cap_size, legend=False)
ax3.set_ylim(0, 38)
ax3.set_yticks([0, 15, 30])
ax3.set_yticklabels([0, 15, 30])
ax3.set_ylabel('mean time (s)')
ax3.set_xticklabels(['bout length'], rotation='horizontal')

line_y = [mean_time_grooming_bout['ctrl_mean'].item() + sem_time_grooming_bout['ctrl_sem'].item() + 2]*2
line_x = [-0.125, 0.125]

ax3.plot(line_x, line_y, color='black', linewidth=1.0)
ax3.annotate('*',
             xy=(0, np.round(mean_time_grooming_bout['ctrl_mean'].item() + sem_time_grooming_bout['ctrl_sem'].item() + 2)),
             xycoords='data',
             ha='center')


incorrect_transitions = ['prop_initiation_incorrect_transitions',
              'prop_skipped_transitions',
              'prop_reversed_transitions',
              'prop_aborted_transitions']

mapping = {transition: i for i, transition in enumerate(incorrect_transitions)}
mean_key = mean_incorrect_transitions_prop_session.measure.map(mapping)
mean_incorrect_transitions_prop_session = mean_incorrect_transitions_prop_session.iloc[mean_key.argsort()]

sem_key = sem_incorrect_transitions_prop_session.measure.map(mapping)
sem_incorrect_transitions_prop_session = sem_incorrect_transitions_prop_session.iloc[sem_key.argsort()]

mean_incorrect_transitions_prop_session.plot.bar(ax=ax4, x='measure', y=['ctrl_mean', 'ko_mean'],
                                                  color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                                  yerr=[sem_incorrect_transitions_prop_session['ctrl_sem'].to_list(),
                                                        sem_incorrect_transitions_prop_session['ko_sem'].to_list()],
                                                  capsize=cap_size)
incorrect_initiation_yoffset = mean_incorrect_transitions_prop_session[
                                   mean_incorrect_transitions_prop_session.measure
                                   == 'prop_initiation_incorrect_transitions']['ko_mean'].item() \
                               + sem_incorrect_transitions_prop_session[
                                   sem_incorrect_transitions_prop_session.measure
                                   == 'prop_initiation_incorrect_transitions']['ko_sem'].item() \
                               + 0.05
skipped_yoffset = mean_incorrect_transitions_prop_session[
                                   mean_incorrect_transitions_prop_session.measure
                                   == 'prop_skipped_transitions']['ctrl_mean'].item() \
                               + sem_incorrect_transitions_prop_session[
                                   sem_incorrect_transitions_prop_session.measure
                                   == 'prop_skipped_transitions']['ctrl_sem'].item() \
                               + 0.05
reversed_yoffset = mean_incorrect_transitions_prop_session[
                                   mean_incorrect_transitions_prop_session.measure
                                   == 'prop_reversed_transitions']['ctrl_mean'].item() \
                               + sem_incorrect_transitions_prop_session[
                                   sem_incorrect_transitions_prop_session.measure
                                   == 'prop_reversed_transitions']['ctrl_sem'].item() \
                               + 0.05
aborted_yoffset = mean_incorrect_transitions_prop_session[
                                   mean_incorrect_transitions_prop_session.measure
                                   == 'prop_aborted_transitions']['ko_mean'].item() \
                               + sem_incorrect_transitions_prop_session[
                                   sem_incorrect_transitions_prop_session.measure
                                   == 'prop_aborted_transitions']['ko_sem'].item() \
                               + 0.05

line_y_incorrect_initiation = [incorrect_initiation_yoffset]*2
line_x_incorrect_initiation = [-0.125, 0.125]

line_y_skipped = [skipped_yoffset]*2
line_x_skipped = [0.875, 1.125]

line_y_reversed = [reversed_yoffset]*2
line_x_reversed = [1.875, 2.125]

line_y_aborted = [aborted_yoffset]*2
line_x_aborted = [2.875, 3.125]

ax4.plot(line_x_incorrect_initiation, line_y_incorrect_initiation, color='black', linewidth=1.0)
ax4.annotate('*',
             xy=(0, incorrect_initiation_yoffset),
             xycoords='data',
             ha='center')

ax4.plot(line_x_skipped, line_y_skipped, color='black', linewidth=1.0)
ax4.annotate('*',
             xy=(1, skipped_yoffset),
             xycoords='data',
             ha='center')

ax4.plot(line_x_reversed, line_y_reversed, color='black', linewidth=1.0)
ax4.annotate('*',
             xy=(2, reversed_yoffset),
             xycoords='data',
             ha='center')

ax4.plot(line_x_aborted, line_y_aborted, color='black', linewidth=1.0)
ax4.annotate('*',
             xy=(3, aborted_yoffset),
             xycoords='data',
             ha='center')

ax4.set_ylim(0, 1)
ax4.set_yticks([0, 0.5, 1])
ax4.set_yticklabels(['0', '50', '100'])
ax4.set_ylabel('% incorrect transitions')
ax4.set_xticklabels(['incorrect\ninitiation', 'skipped', 'reversed', 'aborted'], rotation='horizontal')
ax4.set_xlabel('incorrect transition type')
handles, _ = ax4.get_legend_handles_labels()
labels = ['control', 'Dlx-CKO']
ax4.legend(handles, labels)
ax4.get_legend().set_title(None)


total_transitions = ['total_transitions',
                     'total_incorrect_transitions']

mapping_total_transitions = {transition: i for i, transition in enumerate(total_transitions)}
mean_key_total_transitions = mean_total_transitions_bout.measure.map(mapping_total_transitions)
mean_total_transitions_bout = mean_total_transitions_bout.iloc[mean_key_total_transitions.argsort()]

sem_key_total_transitions = sem_total_transitions_bout.measure.map(mapping_total_transitions)
sem_total_transitions_bout = sem_total_transitions_bout.iloc[sem_key_total_transitions.argsort()]

mean_total_transitions_bout.plot.bar(ax=ax5, y=['ctrl_mean', 'ko_mean'], color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                    yerr=[sem_total_transitions_bout['ctrl_sem'].to_list(),
                                          sem_total_transitions_bout['ko_sem'].to_list()],
                                    capsize=cap_size, legend=False)

total_transitions_yoffset = mean_total_transitions_bout[
                                   mean_total_transitions_bout.measure
                                   == 'total_transitions']['ctrl_mean'].item() \
                               + sem_total_transitions_bout[
                                   sem_total_transitions_bout.measure
                                   == 'total_transitions']['ctrl_sem'].item() \
                               + 0.5
incorrect_transitions_yoffset = mean_total_transitions_bout[
                                   mean_total_transitions_bout.measure
                                   == 'total_incorrect_transitions']['ctrl_mean'].item() \
                               + sem_total_transitions_bout[
                                   sem_total_transitions_bout.measure
                                   == 'total_incorrect_transitions']['ctrl_sem'].item() \
                               + 0.5

line_x_total_transitions = [-0.125, 0.125]
line_y_total_transitions = [total_transitions_yoffset]*2

line_x_incorrect_transitions = [0.875, 1.125]
line_y_incorrect_transitions = [incorrect_transitions_yoffset]*2

ax5.plot(line_x_total_transitions, line_y_total_transitions, color='black', linewidth=1.0)
ax5.annotate('*',
             xy=(0, total_transitions_yoffset),
             xycoords='data',
             ha='center')

ax5.plot(line_x_incorrect_transitions, line_y_incorrect_transitions, color='black', linewidth=1.0)
ax5.annotate('*',
             xy=(1, incorrect_transitions_yoffset),
             xycoords='data',
             ha='center')

ax5.set_ylim(0, 10)
ax5.set_yticks([0, 3, 9])
ax5.set_yticklabels([0, 3, 9])
ax5.set_ylabel('mean per bout')
ax5.set_xticklabels(['total', 'incorrect'], rotation='horizontal')
ax5.set_xlabel('transitions')

plt.tight_layout()
plt.savefig('/Users/Krista/OneDrive - Umich/figures/figures_ai/figure3/fig3_20210506.pdf')
