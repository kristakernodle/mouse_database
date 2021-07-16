import database_pkg as dbpkg
import pandas as pd
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Patch
from datetime import date

from data_visualization.plot_functions import get_mean_sem, genotype_cleanup, Column, create_stacked_bar_chart, \
    format_ax, paired_bar_chart

today_str = dbpkg.Date(date.today().strftime('%Y%m%d')).yyyymmdd

custom_colors = {'Dlx-CKO Control': "#005AB5", "Dlx-CKO": "#DC3220"}

bouts_df = pd.read_sql(dbpkg.db.session.query(dbpkg.Mouse.mouse_id,
                                              dbpkg.Mouse.eartag,
                                              dbpkg.Mouse.sex,
                                              dbpkg.Mouse.birthdate,
                                              dbpkg.Mouse.genotype,
                                              dbpkg.Session.session_id,
                                              dbpkg.Session.session_date,
                                              dbpkg.Session.session_dir,
                                              dbpkg.Session.session_num,
                                              dbpkg.GroomingTrial.grooming_trial_id,
                                              dbpkg.GroomingTrial.trial_num,
                                              dbpkg.GroomingBout.grooming_bout_id,
                                              dbpkg.GroomingBout.bout_length) \
                       .join(dbpkg.Session, dbpkg.Session.mouse_id == dbpkg.Mouse.mouse_id) \
                       .join(dbpkg.GroomingTrial, dbpkg.GroomingTrial.session_id == dbpkg.Session.session_id) \
                       .join(dbpkg.GroomingBout,
                             dbpkg.GroomingBout.grooming_trial_id == dbpkg.GroomingTrial.grooming_trial_id) \
                       .statement,
                       dbpkg.db.session.bind)

bouts_df['bout_duration'] = bouts_df['bout_length']

temp_bouts_df = bouts_df
temp_bouts_df['genotype'] = temp_bouts_df.apply(lambda x: genotype_cleanup(x), axis=1)
temp_bouts_df.to_csv(f'/Users/Krista/OneDrive - Umich/figures/grooming_bouts_{today_str}.csv')

chains_df = pd.read_sql(dbpkg.db.session.query(dbpkg.Mouse.mouse_id,
                                               dbpkg.Mouse.eartag,
                                               dbpkg.Mouse.sex,
                                               dbpkg.Mouse.birthdate,
                                               dbpkg.Mouse.genotype,
                                               dbpkg.Session.session_id,
                                               dbpkg.Session.session_date,
                                               dbpkg.Session.session_dir,
                                               dbpkg.Session.session_num,
                                               dbpkg.GroomingTrial.grooming_trial_id,
                                               dbpkg.GroomingChain.grooming_chain_id,
                                               dbpkg.GroomingChain.start_frame,
                                               dbpkg.GroomingChain.end_frame,
                                               dbpkg.GroomingChain.complete,
                                               dbpkg.GroomingChain.grooming_phase_1,
                                               dbpkg.GroomingChain.grooming_phase_2,
                                               dbpkg.GroomingChain.grooming_phase_3,
                                               dbpkg.GroomingChain.grooming_phase_4,
                                               dbpkg.GroomingChain.num_transitions,
                                               dbpkg.GroomingChain.num_atypical_transitions,
                                               dbpkg.GroomingChain.num_skips,
                                               dbpkg.GroomingChain.num_reverse,
                                               dbpkg.GroomingChain.num_atypical_end) \
                        .join(dbpkg.Session, dbpkg.Session.mouse_id == dbpkg.Mouse.mouse_id) \
                        .join(dbpkg.GroomingTrial, dbpkg.GroomingTrial.session_id == dbpkg.Session.session_id) \
                        .join(dbpkg.GroomingChain,
                              dbpkg.GroomingChain.grooming_trial_id == dbpkg.GroomingTrial.grooming_trial_id) \
                        .statement,
                        dbpkg.db.session.bind)

chains_df.insert(chains_df.shape[1], 'duration_frames',
                 chains_df['end_frame'] - chains_df['start_frame'])
chains_df.insert(chains_df.shape[1], 'duration_seconds',
                 chains_df['duration_frames'] / 100)
chains_df.insert(chains_df.shape[1], 'proportion_atypicalTransitions',
                 chains_df['num_atypical_transitions'] / chains_df['num_transitions'])
chains_df.insert(chains_df.shape[1], 'proportion_skips',
                 chains_df['num_skips'] / chains_df['num_atypical_transitions'])
chains_df.insert(chains_df.shape[1], 'proportion_reverse',
                 chains_df['num_reverse'] / chains_df['num_atypical_transitions'])
chains_df.insert(chains_df.shape[1], 'proportion_atypical_end',
                 chains_df['num_atypical_end'] / chains_df['num_atypical_transitions'])

chains_df['genotype'] = chains_df.apply(lambda x: genotype_cleanup(x), axis=1)
chains_df.to_csv(f'/Users/Krista/OneDrive - Umich/figures/grooming_chains_{today_str}.csv')

chains_only_df = pd.read_sql(dbpkg.db.session.query(
    dbpkg.GroomingTrial.grooming_trial_id,
    dbpkg.GroomingChain.grooming_chain_id,
    dbpkg.GroomingChain.start_frame,
    dbpkg.GroomingChain.end_frame,
    dbpkg.GroomingChain.complete,
    dbpkg.GroomingChain.grooming_phase_1,
    dbpkg.GroomingChain.grooming_phase_2,
    dbpkg.GroomingChain.grooming_phase_3,
    dbpkg.GroomingChain.grooming_phase_4,
    dbpkg.GroomingChain.num_transitions,
    dbpkg.GroomingChain.num_atypical_transitions,
    dbpkg.GroomingChain.num_skips,
    dbpkg.GroomingChain.num_reverse,
    dbpkg.GroomingChain.num_atypical_end) \
                             .join(dbpkg.GroomingChain,
                                   dbpkg.GroomingChain.grooming_trial_id == dbpkg.GroomingTrial.grooming_trial_id).statement,
                             dbpkg.db.session.bind)

chains_only_df.insert(chains_only_df.shape[1], 'chain_duration',
                      (chains_only_df['end_frame'] - chains_only_df['start_frame']) / 100)

chains_by_trial_df = chains_only_df.groupby('grooming_trial_id').agg(sum)
chains_by_trial_df = chains_by_trial_df.rename_axis('grooming_trial_id').reset_index()

trials_df = pd.read_sql(dbpkg.db.session.query(dbpkg.Mouse.mouse_id,
                                               dbpkg.Mouse.eartag,
                                               dbpkg.Mouse.sex,
                                               dbpkg.Mouse.birthdate,
                                               dbpkg.Mouse.genotype,
                                               dbpkg.Session.session_id,
                                               dbpkg.Session.session_date,
                                               dbpkg.Session.session_dir,
                                               dbpkg.Session.session_num,
                                               dbpkg.GroomingTrial.grooming_trial_id,
                                               dbpkg.GroomingTrial.trial_num,
                                               dbpkg.GroomingTrial.trial_length,
                                               dbpkg.GroomingTrial.total_time_grooming,
                                               dbpkg.GroomingTrial.latency_to_onset,
                                               dbpkg.GroomingTrial.num_bouts,
                                               dbpkg.GroomingTrial.num_chains,
                                               dbpkg.GroomingTrial.num_complete_chains,
                                               ) \
                        .join(dbpkg.Session, dbpkg.Session.mouse_id == dbpkg.Mouse.mouse_id) \
                        .join(dbpkg.GroomingTrial, dbpkg.GroomingTrial.session_id == dbpkg.Session.session_id) \
                        .statement,
                        dbpkg.db.session.bind)

temp_trials_df = trials_df
temp_trials_df['genotype'] = temp_trials_df.apply(lambda x: genotype_cleanup(x), axis=1)

trials_with_chains = pd.merge(temp_trials_df, chains_by_trial_df, on=['grooming_trial_id'], how='left')
trials_with_chains['chain_duration'] = trials_with_chains['chain_duration'].fillna(0)

trials_with_chains.insert(trials_with_chains.shape[1], 'num_incomplete_chains',
                          trials_with_chains['num_chains'] - trials_with_chains['num_complete_chains'])

trials_with_chains.insert(trials_with_chains.shape[1], 'nonchain_duration',
                          trials_with_chains['total_time_grooming'] - trials_with_chains['chain_duration'])

trials_with_chains.insert(trials_with_chains.shape[1], 'transitions_perChain',
                          trials_with_chains['num_transitions'] / trials_with_chains['num_chains'])

trials_with_chains.insert(trials_with_chains.shape[1], 'atypicalTransitions_perChain',
                          trials_with_chains['num_atypical_transitions'] / trials_with_chains['num_chains'])

trials_with_chains.insert(trials_with_chains.shape[1], 'num_typical_transitions',
                          trials_with_chains['num_transitions'] - trials_with_chains['num_atypical_transitions'])

trials_with_chains.insert(trials_with_chains.shape[1], 'typicalTransitions_perChain',
                          trials_with_chains['num_typical_transitions'] / trials_with_chains['num_chains'])

trials_with_chains.insert(trials_with_chains.shape[1], 'totalGrooming_percentTrial',
                          (trials_with_chains['total_time_grooming'] / trials_with_chains['trial_length']) * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'nonChainGrooming_percentTotalGrooming',
                          (trials_with_chains['nonchain_duration'] / trials_with_chains['total_time_grooming']) * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'chainGrooming_percentTotalGrooming',
                          (trials_with_chains['chain_duration'] / trials_with_chains['total_time_grooming']) * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'chains_perMin',
                          trials_with_chains['num_chains'] / (trials_with_chains['total_time_grooming'] / 60))

trials_with_chains.insert(trials_with_chains.shape[1], 'bouts_perMin',
                          trials_with_chains['num_bouts'] / (trials_with_chains['total_time_grooming'] / 60))

trials_with_chains.insert(trials_with_chains.shape[1], 'chainGrooming_percentTrial',
                          (trials_with_chains['chain_duration'] / (trials_with_chains['trial_length']) * 100))

trials_with_chains.insert(trials_with_chains.shape[1], 'nonChainGrooming_percentTrial',
                          (trials_with_chains['nonchain_duration'] / (trials_with_chains['trial_length']) * 100))

trials_with_chains.insert(trials_with_chains.shape[1], 'typicalTransitions_percentTotal',
                          trials_with_chains['num_typical_transitions'] / (trials_with_chains['num_transitions'] / 60))

trials_with_chains.insert(trials_with_chains.shape[1], 'atypicalTransitions_percentTotal',
                          trials_with_chains['num_atypical_transitions'] / (trials_with_chains['num_transitions'] / 60))

trials_with_chains.insert(trials_with_chains.shape[1], 'phase1_percentTotalPhases',
                          trials_with_chains['grooming_phase_1'] / trials_with_chains['num_transitions'] * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'phase2_percentTotalPhases',
                          trials_with_chains['grooming_phase_2'] / trials_with_chains['num_transitions'] * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'phase3_percentTotalPhases',
                          trials_with_chains['grooming_phase_3'] / trials_with_chains['num_transitions'] * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'phase4_percentTotalPhases',
                          trials_with_chains['grooming_phase_4'] / trials_with_chains['num_transitions'] * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'skips_percentAtypicalTransitions',
                          trials_with_chains['num_skips'] / trials_with_chains['num_atypical_transitions'] * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'reverse_percentAtypicalTransitions',
                          trials_with_chains['num_reverse'] / trials_with_chains['num_atypical_transitions'] * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'atypicalEnd_percentAtypicalTransitions',
                          trials_with_chains['num_atypical_end'] / trials_with_chains['num_atypical_transitions'] * 100)

trials_with_chains.to_csv(f'/Users/Krista/OneDrive - Umich/figures/grooming_chains_nonchains_{today_str}.csv')
trials_with_chains_mean_sem = trials_with_chains.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])


# Plotting


def format_h_ax(axis, xlim, xticks, xlabel, xticklabels=None, title=None, titleloc='center'):
    if xticklabels is None:
        xticklabels = xticks

    axis.set_xlim(xlim[0], xlim[1])
    axis.set_xticks(xticks)
    axis.set_xticklabels(xticklabels)
    axis.set_xlabel(xlabel)
    axis.set_ylim(-0.6, 2)
    axis.set_yticks([0, 1])
    axis.set_yticklabels(['Control', 'Dlx-CKO'])
    axis.spines['top'].set_visible(False)
    axis.spines['right'].set_visible(False)
    axis.tick_params(axis='y', which='both', left=False)
    axis.set_title(title, loc=titleloc)
    return axis


def create_legend_patches(ordered_columns):
    patches = []
    for column in ordered_columns:
        patches.append(Patch(facecolor='k',
                             edgecolor='w',
                             label=column.label,
                             hatch=column.hatch,
                             alpha=column.alpha))
    return patches


fig = plt.figure()
w = 5.5
fig.set_figwidth(w)
fig.set_dpi(1000)
cap_size = 4
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"
plt.rcParams['xtick.major.pad'] = -0.5
plt.rcParams['ytick.major.pad'] = -0.5
color_dict = {"Control": custom_colors["Dlx-CKO Control"],
              "Dlx-CKO": custom_colors["Dlx-CKO"]}

totalGrooming_gs = gridspec.GridSpec(1, 2)
totalGrooming_nonChain_ax = fig.add_subplot(totalGrooming_gs[0])
totalGrooming_chain_ax = fig.add_subplot(totalGrooming_gs[1])

initiationsPerMin_gs = gridspec.GridSpec(1, 2)
initiationsPerMin_nonChain_ax = fig.add_subplot(initiationsPerMin_gs[0])
initiationsPerMin_chain_ax = fig.add_subplot(initiationsPerMin_gs[1])

duration_gs = gridspec.GridSpec(1, 2)
duration_nonChain_ax = fig.add_subplot(duration_gs[0])
duration_chain_ax = fig.add_subplot(duration_gs[1])

chainQuantity_gs = gridspec.GridSpec(1, 2)
chainQuantity_nonChain_ax = fig.add_subplot(chainQuantity_gs[0])
chainQuantity_chain_ax = fig.add_subplot(chainQuantity_gs[1])

numTransitions_gs = gridspec.GridSpec(1, 2)
numTransitions_nonChain_ax = fig.add_subplot(numTransitions_gs[0])
numTransitions_chain_ax = fig.add_subplot(numTransitions_gs[1])

distributionTransition_gs = gridspec.GridSpec(1, 1)
distributionTransition_ax = fig.add_subplot(distributionTransition_gs[0])

distributionPhases_gs = gridspec.GridSpec(1, 1)
distributionPhases_ax = fig.add_subplot(distributionPhases_gs[0])

# totalGrooming_nonChain_ax = plt.subplot2grid((4, 6), (0, 4))
# totalGrooming_chain_ax = plt.subplot2grid((4, 6), (0, 5))
# initiationsPerMin_nonChain_ax = plt.subplot2grid((4, 6), (1, 4), colspan=2)
# duration_nonChain_ax = plt.subplot2grid((4, 6), (2, 0), colspan=2)
# chainQuantity_nonChain_ax = plt.subplot2grid((4, 6), (2, 2), colspan=2)
# numTransitions_nonChain_ax = plt.subplot2grid((4, 6), (2, 4), colspan=2)
# distributionTransition_ax = plt.subplot2grid((4, 6), (3, 0), colspan=3)
# distributionPhases_ax = plt.subplot2grid((4, 6), (3, 3), colspan=3)

columns_dict = {
    totalGrooming_nonChain_ax: [Column('nonChainGrooming_percentTrial', 'non-chain', hatch='///', alpha=None)],
    totalGrooming_chain_ax: [Column('chainGrooming_percentTrial', 'chain', hatch=None, alpha=None)],
    initiationsPerMin_nonChain_ax: [Column('bouts_perMin', 'non-chain', hatch='///', alpha=None)],
    initiationsPerMin_chain_ax: [Column('chains_perMin', 'chain', hatch=None, alpha=None)],
    duration_nonChain_ax: [Column('nonchain_duration', 'non-chain', hatch='///', alpha=None)],
    duration_chain_ax: [Column('chain_duration', 'chain', hatch=None, alpha=None)],
    chainQuantity_nonChain_ax: [Column("num_complete_chains", 'complete', hatch=None, alpha=None)],
    chainQuantity_chain_ax: [Column('num_incomplete_chains', 'incomplete', hatch=None, alpha=0.5)],
    numTransitions_nonChain_ax: [Column('num_typical_transitions', 'typical', hatch=None, alpha=1)],
    numTransitions_chain_ax: [Column('num_atypical_transitions', 'atypical', hatch=None, alpha=0.5)],
    distributionTransition_ax: [Column("skips_percentAtypicalTransitions", 'skips', hatch=None, alpha=1),
                                Column("reverse_percentAtypicalTransitions", 'reverses', hatch=None, alpha=0.6),
                                Column('atypicalEnd_percentAtypicalTransitions', 'premature\ntermination', hatch=None,
                                       alpha=0.3)],
    distributionPhases_ax: [Column("grooming_phase_1", 'ellipse', hatch=None, alpha=1),
                            Column("grooming_phase_2", 'unilteral\nstrokes', hatch=None, alpha=1),
                            Column("grooming_phase_3", 'bilateral\nstrokes', hatch=None, alpha=1),
                            Column("grooming_phase_4", 'body licks', hatch=None, alpha=1)]
}

# Total Grooming Time (Fig 3B)

totalGrooming_nonChain_ax = paired_bar_chart(totalGrooming_nonChain_ax,
                                             columns_dict,
                                             trials_with_chains_mean_sem,
                                             'time spent\n(% of trial)',
                                             [0, 31],
                                             [5, 15, 25],
                                             title='grooming quantity')

totalGrooming_chain_ax = paired_bar_chart(totalGrooming_chain_ax,
                                          columns_dict,
                                          trials_with_chains_mean_sem,
                                          None,
                                          [0, 5],
                                          [2, 4])
totalGrooming_chain_ax.yaxis.set_label_position("right")
totalGrooming_chain_ax.yaxis.tick_left()
# totalGrooming_orderedColumns = columns_dict[totalGrooming_nonChain_ax]
#
# totalGrooming_mean, totalGrooming_sem = get_mean_sem(trials_with_chains_mean_sem,
#                                                      totalGrooming_orderedColumns)
# totalGrooming_mean = totalGrooming_mean.set_index(('genotype',)).transpose().reset_index().set_index('level_0')
# totalGrooming_sem = totalGrooming_sem.set_index(('genotype',)).transpose().reset_index().set_index('level_0')
#
# totalGrooming_x = list(range(len(totalGrooming_mean)))
#
# totalGrooming_nonChain_ax = create_stacked_bar_chart(totalGrooming_nonChain_ax,
#                                             totalGrooming_mean,
#                                             totalGrooming_sem,
#                                             totalGrooming_orderedColumns,
#                                             )
#
# legend_elements = create_legend_patches(totalGrooming_orderedColumns)
# totalGrooming_nonChain_ax.legend(handles=legend_elements,
#                             loc='upper center',
#                             frameon=False,
#                             fancybox=False,
#                             fontsize='small')

# Initiations per Minute Grooming (Fig 3C)

initiationsPerMin_nonChain_ax = paired_bar_chart(initiationsPerMin_nonChain_ax,
                                                 columns_dict,
                                                 trials_with_chains_mean_sem,
                                                 'initiations\nper min grooming',
                                                 [0, 5],
                                                 [2, 4],
                                                 title='grooming frequency')
initiationsPerMin_chain_ax = paired_bar_chart(initiationsPerMin_chain_ax,
                                              columns_dict,
                                              trials_with_chains_mean_sem,
                                              None,
                                              [0, 5.2],
                                              [2, 4])
bar_width = 0.35
initiationsPerMin_nonChain_ax.plot([-bar_width / 2, bar_width / 2], [4.75, 4.75], color='black', linewidth=1.0)
initiationsPerMin_nonChain_ax.annotate('*',
                                       xy=(0, 4.75),
                                       xycoords='data',
                                       ha='center')

initiationsPerMin_chain_ax.plot([-bar_width / 2, bar_width / 2], [1.8, 1.8], color='black', linewidth=1.0)
initiationsPerMin_chain_ax.annotate('*',
                                       xy=(0, 1.8),
                                       xycoords='data',
                                       ha='center')

initiationsPerMin_chain_ax.yaxis.set_label_position("right")
initiationsPerMin_chain_ax.yaxis.tick_left()
initiationsPerMin_chain_ax.yaxis.set_tick_params(width=0, length=0, labelleft=False)
initiationsPerMin_chain_ax.spines['left'].set_visible(False)
initiationsPerMin_chain_ax.spines['right'].set_visible(False)
# initiationsPerMin_orderedColumns = columns_dict[initiationsPerMin_nonChain_ax]
# initiations_mean, initiations_sem = get_mean_sem(trials_with_chains_mean_sem,
#                                                  initiationsPerMin_orderedColumns)
# initiationsPerMin_nonChain_ax = create_stacked_bar_chart(initiationsPerMin_nonChain_ax,
#                                                 initiations_mean,
#                                                 initiations_sem,
#                                                 initiationsPerMin_orderedColumns)
#
# initiationsPerMin_nonChain_ax = format_ax(initiationsPerMin_nonChain_ax, ylim=[0, 6], yticks=[2, 4, 6],
#                                  ylabel='initiations\n(per min grooming)', title='grooming frequency',
#                                  titleloc='right')
#
# initiationsPerMin_nonChain_ax.plot(x=[])

# Duration (Fig 3D)

duration_nonChain_ax = paired_bar_chart(duration_nonChain_ax,
                                        columns_dict,
                                        trials_with_chains_mean_sem,
                                        'duration (s)',
                                        [0, 360],
                                        [100, 200, 300],
                                        title='uninterrupted grooming')
duration_chain_ax = paired_bar_chart(duration_chain_ax,
                                     columns_dict,
                                     trials_with_chains_mean_sem,
                                     None,
                                     [0, 50],
                                     [15, 30, 45])
duration_chain_ax.yaxis.set_label_position("right")
duration_chain_ax.yaxis.tick_left()

# duration_orderedColumns = columns_dict[duration_nonChain_ax]
# duration_mean, duration_sem = get_mean_sem(trials_with_chains_mean_sem,
#                                            duration_orderedColumns)
# duration_nonChain_ax = create_stacked_bar_chart(duration_nonChain_ax,
#                                        duration_mean,
#                                        duration_sem,
#                                        duration_orderedColumns)
# duration_nonChain_ax = format_ax(duration_nonChain_ax, ylim=[0, 360], yticks=[100, 200, 300], ylabel='duration (seconds)',
#                         title='uninterrupted grooming', titleloc='right')

# Syntactic chains (Fig 3E)
chainQuantity_nonChain_ax = paired_bar_chart(chainQuantity_nonChain_ax,
                                             columns_dict,
                                             trials_with_chains_mean_sem,
                                             '# of chains\n(per trial)',
                                             [0, 3.75],
                                             [1, 2, 3],
                                             title='syntactic chains')
chainQuantity_chain_ax = paired_bar_chart(chainQuantity_chain_ax,
                                          columns_dict,
                                          trials_with_chains_mean_sem,
                                          None,
                                          [0, 1],
                                          [0.2, 0.4, 0.8])
chainQuantity_chain_ax.yaxis.set_label_position("right")
chainQuantity_chain_ax.yaxis.set_tick_params(width=0, length=0, labelleft=False)
chainQuantity_chain_ax.spines['left'].set_visible(False)
chainQuantity_chain_ax.spines['right'].set_visible(False)
# chainQuantity_nonChain_ax.set_title('syntactic chains', fontdict={'fontsize': 'medium'})
# numberChains_orderedColumns = columns_dict[chainQuantity_nonChain_ax]
# numberChains_mean, numberChains_sem = get_mean_sem(trials_with_chains_mean_sem,
#                                                    numberChains_orderedColumns)
# chainQuantity_nonChain_ax = create_stacked_bar_chart(chainQuantity_nonChain_ax,
#                                             numberChains_mean,
#                                             numberChains_sem,
#                                             numberChains_orderedColumns)
# chainQuantity_nonChain_ax = format_ax(chainQuantity_nonChain_ax, ylim=[0, 4.5], yticks=[1, 2, 3, 4],
#                              ylabel='number of chains\n(per trial)', title='syntactic chains')
#
# legend_elements = create_legend_patches(numberChains_orderedColumns)
# chainQuantity_nonChain_ax.legend(handles=legend_elements,
#                         loc='right',
#                         frameon=False,
#                         fancybox=False,
#                         fontsize='small')

# Number of transitions

numTransitions_nonChain_ax = paired_bar_chart(numTransitions_nonChain_ax,
                                              columns_dict,
                                              trials_with_chains_mean_sem,
                                              '# of transitions\nper trial',
                                              [0, 10],
                                              [3, 6, 9],
                                              title='phase transitions')
numTransitions_chain_ax = paired_bar_chart(numTransitions_chain_ax,
                                           columns_dict,
                                           trials_with_chains_mean_sem,
                                           None,
                                           [0, 10],
                                           [3, 6, 9])
numTransitions_chain_ax.yaxis.set_label_position("right")
numTransitions_chain_ax.spines['left'].set_visible(False)
numTransitions_chain_ax.spines['right'].set_visible(False)
numTransitions_chain_ax.yaxis.set_tick_params(width=0, length=0, labelleft=False)

# numberTransitions_orderedColumns = columns_dict[numTransitions_nonChain_ax]
# numberTransitions_mean, numberTransitions_sem = get_mean_sem(trials_with_chains_mean_sem,
#                                                              numberTransitions_orderedColumns)
# numTransitions_nonChain_ax = create_stacked_bar_chart(numTransitions_nonChain_ax,
#                                              numberTransitions_mean,
#                                              numberTransitions_sem,
#                                              numberTransitions_orderedColumns)
# numTransitions_nonChain_ax = format_ax(numTransitions_nonChain_ax,
#                               ylim=[0, 17],
#                               yticks=[5, 10, 15],
#                               ylabel="number of transitions\n(per trial)",
#                               title='phase transitions')
#
# legend_elements = create_legend_patches(numberChains_orderedColumns)
# numTransitions_nonChain_ax.legend(handles=legend_elements,
#                         loc='right',
#                         frameon=False,
#                         fancybox=False,
#                         fontsize='small')

# Distribution of atypical transitions (Fig 3G)
distributionTransition_ax = paired_bar_chart(distributionTransition_ax,
                                             columns_dict,
                                             trials_with_chains_mean_sem,
                                             'proportion of transitions\n(% of atypical transitions)',
                                             [0, 75],
                                             [20, 40, 60],
                                             title='distribution of atypical transitions')
# distributionTransition_ax.tick_params('x', labelrotation=90)
distributionPhases_ax = paired_bar_chart(distributionPhases_ax,
                                         columns_dict,
                                         trials_with_chains_mean_sem,
                                         '# of occurences\n(per trial)',
                                         [0, 5],
                                         [2, 4],
                                         title='distribution of grooming phases')
# distributionPhases_ax.set_title('distribution of grooming phases', fontdict={'fontsize': 'medium'})

# distributionTransitions_orderedColumns = columns_dict[distributionTransition_ax]
# distributionTransitions_mean, distributionTransitions_sem = get_mean_sem(trials_with_chains_mean_sem,
#                                                                          distributionTransitions_orderedColumns)
# distributionTransition_ax = create_stacked_bar_chart(distributionTransition_ax,
#                                                      distributionTransitions_mean,
#                                                      distributionTransitions_sem,
#                                                      distributionTransitions_orderedColumns)
# distributionTransition_ax = format_ax(distributionTransition_ax,
#                                       ylim=[0, 110],
#                                       yticks=[25, 50, 75, 100],
#                                       ylabel='proportion of transitions\n(% of atypical transitions)',
#                                       title='distribution of\natypical transitions',
#                                       titleloc='right')
#
# legend_elements = create_legend_patches(distributionTransitions_orderedColumns)
# distributionTransition_ax.legend(handles=legend_elements,
#                                  loc='upper center',
#                                  frameon=False,
#                                  fancybox=False,
#                                  fontsize='small')

oneThird = float(1 / 3)
twoThird = float(2 / 3)

totalGrooming_gs.tight_layout(fig, rect=[0, 0.75, 0.5, 1], pad=0.2)
initiationsPerMin_gs.tight_layout(fig, rect=[0.5, 0.75, 1, 1], pad=0.2, w_pad=1)
duration_gs.tight_layout(fig, rect=[0, 0.5, 0.5, 0.75], pad=0.2)
chainQuantity_gs.tight_layout(fig, rect=[0.5, 0.5, 1, 0.75], pad=0.2, w_pad=1)
numTransitions_gs.tight_layout(fig, rect=[0, 0.25, 0.5, 0.5], pad=0.2, w_pad=1)
distributionTransition_gs.tight_layout(fig, rect=[0.5, 0.25, 1, 0.5], pad=0.2)
distributionPhases_gs.tight_layout(fig, rect=[0, 0, 1, 0.25], pad=0.2)

# third_col_left = min(totalGrooming_gs.left, initiationsPerMin_gs.left, numTransitions_gs.left)
# totalGrooming_gs.update(left=third_col_left)
# initiationsPerMin_gs.update(left=third_col_left)
# numTransitions_gs.update(left=third_col_left)

# plt.tight_layout()
plt.savefig(f'/Users/Krista/OneDrive - Umich/figures/figures_ai/figure3/fig3_{today_str}.pdf')
plt.close('all')