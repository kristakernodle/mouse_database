import database_pkg as dbpkg
import pandas as pd
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Patch
from datetime import date

from data_visualization.plot_functions import genotype_cleanup, Column, paired_bar_chart

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
                                              dbpkg.GroomingBout.bout_string,
                                              dbpkg.GroomingBout.bout_length) \
                       .join(dbpkg.Session, dbpkg.Session.mouse_id == dbpkg.Mouse.mouse_id) \
                       .join(dbpkg.GroomingTrial, dbpkg.GroomingTrial.session_id == dbpkg.Session.session_id) \
                       .join(dbpkg.GroomingBout,
                             dbpkg.GroomingBout.grooming_trial_id == dbpkg.GroomingTrial.grooming_trial_id) \
                       .statement,
                       dbpkg.db.session.bind)

bouts_only_df = pd.read_sql(dbpkg.db.session.query(dbpkg.GroomingTrial.grooming_trial_id,
                                                   dbpkg.GroomingBout.grooming_bout_id,
                                                   dbpkg.GroomingBout.bout_string,
                                                   dbpkg.GroomingBout.bout_length) \
                            .join(dbpkg.GroomingBout,
                                  dbpkg.GroomingBout.grooming_trial_id == dbpkg.GroomingTrial.grooming_trial_id) \
                            .statement,
                            dbpkg.db.session.bind)


def count_boutPhases(bout_string_srs: pd.Series, phase_num):
    phase_count = []
    for item in bout_string_srs:
        item_list = item.strip().split('-')
        while '' in item_list:
            item_list.remove('')
        phase_count.append(list(map(int, item_list)).count(phase_num))
    return phase_count


bouts_only_df.insert(bouts_only_df.shape[1], 'phase_1', count_boutPhases(bouts_only_df['bout_string'], phase_num=1))
bouts_only_df.insert(bouts_only_df.shape[1], 'phase_2', count_boutPhases(bouts_only_df['bout_string'], phase_num=2))
bouts_only_df.insert(bouts_only_df.shape[1], 'phase_3', count_boutPhases(bouts_only_df['bout_string'], phase_num=3))
bouts_only_df.insert(bouts_only_df.shape[1], 'phase_4', count_boutPhases(bouts_only_df['bout_string'], phase_num=4))

bouts_df['bout_duration'] = bouts_df['bout_length']

temp_bouts_df = bouts_only_df
bouts_df['genotype'] = bouts_df.apply(lambda x: genotype_cleanup(x), axis=1)
bouts_df.to_csv(f'/Users/Krista/OneDrive - Umich/figures/grooming_bouts_{today_str}.csv')

temp_bouts_df = temp_bouts_df.groupby('grooming_trial_id').agg(sum)
temp_bouts_df = temp_bouts_df.rename_axis('grooming_trial_id').reset_index()

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

trials_with_bouts = pd.merge(temp_trials_df, temp_bouts_df, on=['grooming_trial_id'], how='left', validate="1:m")

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

trials_with_chains.insert(trials_with_chains.shape[1], 'totalBoutsChains_perMin',
                          (trials_with_chains['num_chains'] + trials_with_chains['num_bouts']) /
                          (trials_with_chains['total_time_grooming'] / 60))

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

def get_experimentLeg(series):
    out_list = []
    for item in series:
        if item.endswith('G4'):
            out_list.append(1)
            continue
        out_list.append(0)
    return out_list


trials_with_chains.insert(trials_with_chains.shape[1], 'experimentLeg',
                          get_experimentLeg(trials_with_chains['session_dir']))

trials_with_chains.to_csv(f'/Users/Krista/OneDrive - Umich/figures/grooming_chains_nonchains_{today_str}.csv')
trials_with_chains_mean_sem = trials_with_chains.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])

trials_with_bouts_mean_sem = trials_with_bouts.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])
trials_with_bouts.to_csv(f'/Users/Krista/OneDrive - Umich/figures/grooming_trials_bouts_{today_str}.csv')


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
w = 3.54
fig.set_figwidth(w)
fig.set_dpi(1000)
cap_size = 4
bar_width = 0.3
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"
plt.rcParams['xtick.major.pad'] = -0.5
plt.rcParams['ytick.major.pad'] = -0.5
color_dict = {"control": custom_colors["Dlx-CKO Control"],
              "Dlx-CKO": custom_colors["Dlx-CKO"]}

numTransitions_gs = gridspec.GridSpec(1, 1)
numTransitions_ax = fig.add_subplot(numTransitions_gs[0])
# numTransitions_chain_ax = fig.add_subplot(numTransitions_gs[1])

distributionTransition_gs = gridspec.GridSpec(1, 1)
distributionTransition_ax = fig.add_subplot(distributionTransition_gs[0])

columns_dict = {
    numTransitions_ax: [Column('num_typical_transitions', 'typical', hatch=None, alpha=1),
                        Column('num_atypical_transitions', 'atypical', hatch=None, alpha=0.5)],
    distributionTransition_ax: [Column("skips_percentAtypicalTransitions", 'skip', hatch=None, alpha=1),
                                Column("reverse_percentAtypicalTransitions", 'reverse', hatch=None, alpha=0.6),
                                Column('atypicalEnd_percentAtypicalTransitions', 'premature\ntermination', hatch=None,
                                alpha=0.3)]}

# Number of transitions

numTransitions_ax = paired_bar_chart(numTransitions_ax,
                                              columns_dict,
                                              trials_with_chains_mean_sem,
                                              'transitions/trial',
                                              [0, 10],
                                              [3, 6, 9],
                                              title=None)

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
                                             '% atypical transitions',
                                             [0, 75],
                                             [20, 40, 60],
                                             title=None)
# distributionTransition_ax.tick_params('x', labelrotation=90)
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
numTransitions_gs.tight_layout(fig, rect=[0, 0.5, 1, 1], pad=0.2, w_pad=1)
distributionTransition_gs.tight_layout(fig, rect=[0, 0, 1, 0.5], pad=0.2)
fig.savefig(f'/Users/Krista/OneDrive - Umich/figures/figures_ai/figure4/suppfig1_{today_str}.pdf')
plt.close('all')