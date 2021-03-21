from database_pkg import Experiment, Session, GroomingSummary, Mouse
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt

exp = Experiment.get_by_name('dlxCKO-grooming')

data_by_bout = list()

for session in exp.sessions:

    mouse = Mouse.query.get(session.mouse_id)

    total_time_grooming = 0
    num_bouts = 0
    for groom_sum in GroomingSummary.query.filter_by(session_id=session.session_id).all():
        total_time_grooming += groom_sum.total_time_grooming
        num_bouts += groom_sum.num_bouts

        for bout in groom_sum.bouts:
            data_by_bout.append({'bout_id': bout.grooming_bout_id,
                                 'session_id': session.session_id,
                                 'genotype': mouse.genotype,
                                 'bout_time': (bout.bout_end - bout.bout_start) / 100,
                                 'total_transitions': bout.total_num_transitions,
                                 'total_incorrect_transitions': bout.num_incorrect_transitions,
                                 'prop_initiation_incorrect_transitions': sum(
                                    bout.initiation_incorrect_transitions.values()) / bout.num_incorrect_transitions,
                                 'prop_skipped_transitions': sum(
                                    bout.skipped_transitions.values()) / bout.num_incorrect_transitions,
                                 'prop_reversed_transitions': sum(
                                    bout.reversed_transitions.values()) / bout.num_incorrect_transitions,
                                 'prop_aborted_transitions': sum(
                                    bout.aborted_transitions.values()) / bout.num_incorrect_transitions
                                 })

by_bout_df = pd.DataFrame.from_records(data_by_bout)

agg_by_bout = by_bout_df.groupby("genotype").agg([np.mean, stats.sem])
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

agg_by_session = by_bout_df.groupby(["session_id", 'genotype']).agg(np.sum).reset_index()
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

mean_total_incorrect_transitions_session = session_mean_plot_df[session_mean_plot_df.measure == "total_incorrect_transitions"]
sem_total_incorrect_transitions_session = session_sem_plot_df[session_sem_plot_df.measure == "total_incorrect_transitions"]

mean_total_transitions_session = session_mean_plot_df[session_mean_plot_df.measure == "total_transitions"]
sem_total_transitions_session = session_sem_plot_df[session_sem_plot_df.measure == "total_transitions"]

mean_incorrect_transitions_prop_session = session_mean_plot_df[session_mean_plot_df.measure.isin(["prop_initiation_incorrect_transitions",
                                                                                       "prop_skipped_transitions",
                                                                                       "prop_reversed_transitions",
                                                                                       "prop_aborted_transitions"])]
sem_incorrect_transitions_prop_session = session_sem_plot_df[session_sem_plot_df.measure.isin(["prop_initiation_incorrect_transitions",
                                                                                       "prop_skipped_transitions",
                                                                                       "prop_reversed_transitions",
                                                                                       "prop_aborted_transitions"])]
# Plotting

fig, ax = plt.subplots()
w = 8
h = 8
fig.set_figwidth(w)
fig.set_figheight(h)
fig.set_dpi(600)

ax1 = plt.subplot2grid((5, 2), (0, 0))
ax2 = plt.subplot2grid((5, 2), (0, 1))
ax3 = plt.subplot2grid((5, 2), (1, 0))
ax4 = plt.subplot2grid((5, 2), (1, 1))
ax5 = plt.subplot2grid((5, 2), (2, 0))
ax6 = plt.subplot2grid((5, 2), (2, 1))
ax7 = plt.subplot2grid((5, 2), (3, 0), colspan=2)
ax8 = plt.subplot2grid((5, 2), (4, 0), colspan=2)

mean_time_grooming_session.plot.bar(ax=ax1, y=['ctrl_mean', 'ko_mean'], color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                    yerr=[sem_time_grooming_session['ctrl_sem'], sem_time_grooming_session['ko_sem']],
                                    capsize=2, width=1)

mean_total_incorrect_transitions_session.plot.bar(ax=ax3, y=['ctrl_mean', 'ko_mean'],
                                                  color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                                  yerr=[sem_total_incorrect_transitions_session['ctrl_sem'],
                                                        sem_total_incorrect_transitions_session['ko_sem']],
                                                  capsize=2, width=1)

mean_total_transitions_session.plot.bar(ax=ax5, y=['ctrl_mean', 'ko_mean'],
                                                  color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                                  yerr=[sem_total_transitions_session['ctrl_sem'],
                                                        sem_total_transitions_session['ko_sem']],
                                                  capsize=2, width=1)

mean_incorrect_transitions_prop_session.plot.bar(ax=ax7, x='measure', y=['ctrl_mean', 'ko_mean'],
                                                  color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                                  yerr=sem_incorrect_transitions_prop_session['ctrl_sem'].to_list().append(sem_incorrect_transitions_prop_session['ko_sem'].to_list()),
                                                  capsize=2, width=1)

mean_time_grooming_bout.plot.bar(ax=ax2, y=['ctrl_mean', 'ko_mean'], color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                    yerr=[sem_time_grooming_bout['ctrl_sem'], sem_time_grooming_bout['ko_sem']],
                                    capsize=2, width=1)

mean_total_incorrect_transitions_bout.plot.bar(ax=ax4, y=['ctrl_mean', 'ko_mean'],
                                                  color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                                  yerr=[sem_total_incorrect_transitions_bout['ctrl_sem'],
                                                        sem_total_incorrect_transitions_bout['ko_sem']],
                                                  capsize=2, width=1)

mean_total_transitions_bout.plot.bar(ax=ax6, y=['ctrl_mean', 'ko_mean'],
                                                  color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                                  yerr=[sem_total_transitions_bout['ctrl_sem'],
                                                        sem_total_transitions_bout['ko_sem']],
                                                  capsize=2)

mean_incorrect_transitions_prop_bout.plot.bar(ax=ax8, x='measure', y=['ctrl_mean', 'ko_mean'],
                                                  color={"ctrl_mean": 'b', "ko_mean": 'r'},
                                                  yerr=[sem_incorrect_transitions_prop_bout['ctrl_sem'].to_list(),
                                                        sem_incorrect_transitions_prop_bout['ko_sem'].to_list()],
                                                  capsize=2)


# fig, ax = plt.subplots(2, 2)
#
# mean_num_bouts.plot.bar(ax=ax[0][0], y=['ctrl_mean', 'ko_mean'], color={"ctrl_mean": 'b', "ko_mean": 'r'},
#                         yerr=[sem_num_bouts['ctrl_sem'], sem_num_bouts['ko_sem']], capsize=2, width=1)
# ax[0][0].ylabel("mean bouts per session")
# ax[0][0].xticks(ticks=[0], labels="")
# ax[0][0].xlabel("")
# ax[0][0].yticks([0, 10, 20], [0, 10, 20])
#
# mean_time_grooming.plot.bar(ax=ax[0][1], y=['ctrl_mean', 'ko_mean'], color={"ctrl_mean": 'b', "ko_mean": 'r'},
#                             yerr=[sem_time_grooming['ctrl_sem'], sem_time_grooming['ko_sem']], capsize=2, width=1)
# ax[0][1].ylabel("mean grooming time (s) per session")
# ax[0][1].xticks(ticks=[0], labels="")
# ax[0][1].xlabel("")
# ax[0][0].yticks([0, 10, 20], [0, 10, 20])
