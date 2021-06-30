import database_pkg as dbpkg
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Patch
from datetime import date

today_str = dbpkg.Date(date.today().strftime('%Y%m%d')).yyyymmdd


def genotype_cleanup(df_row):
    if df_row['genotype'] == 'Dlx-CKO Control':
        return 'Control'
    else:
        return 'Dlx-CKO'


custom_colors = {'Dlx-CKO Control': "#005AB5", "Dlx-CKO": "#DC3220"}

exp = dbpkg.Experiment.get_by_name('dlxCKO-grooming')

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
bouts_mean_sem = bouts_df.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])
bouts_mean_sem_transpose = bouts_mean_sem.transpose().reset_index()

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
temp_trials_df.to_csv(f'/Users/Krista/OneDrive - Umich/figures/grooming_trials_{today_str}.csv')

trials_mean_sem = trials_df.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])
trials_mean_sem_transpose = trials_mean_sem.transpose().reset_index()

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
                        .filter(dbpkg.Experiment.experiment_id == exp.experiment_id).statement,
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

chains_mean_sem = chains_df.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])
chains_mean_sem_transpose = chains_mean_sem.transpose().reset_index()
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

trials_with_chains = pd.merge(temp_trials_df, chains_by_trial_df, on=['grooming_trial_id'], how='left')
trials_with_chains['chain_duration'] = trials_with_chains['chain_duration'].fillna(0)

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
trials_with_chains_mean_sem_transpose = trials_with_chains_mean_sem.transpose().reset_index()


# Plotting
class Column:
    def __init__(self, name, hatch):
        self.name = name
        self.hatch = hatch

    def __repr__(self):
        return self.name


def get_mean_sem(agg_df, columns):
    columnTups_mean = [(column, "mean") for column in columns]
    columnTups_sem = [(column, "sem") for column in columns]
    mean = agg_df[columnTups_mean]
    sem = agg_df[columnTups_sem]
    return mean.reset_index(), sem.reset_index()


def create_stacked_bar_chart(axis, mean_df, sem_df, ordered_columns):
    if len(ordered_columns) == 2:
        errorbar_x = ([-0.1, 0.9], [0.1, 1.1])
    elif len(ordered_columns) == 3:
        errorbar_x = ([-0.1, 0.9], [0, 1], [0.1, 1.1])
    else:
        errorbar_x = None
        print('errorbar_x undefined')
        breakpoint()

    for index, column in enumerate(ordered_columns):
        if index == 0:
            bottom = [index, index]
        elif index == 1:
            bottom = mean_df[(ordered_columns[0].name, 'mean')]
        elif index == 2:
            bottom = mean_df[(ordered_columns[0].name, 'mean')] + mean_df[(ordered_columns[1].name, 'mean')]

        if column.hatch is None:
            axis.bar([0, 1],
                     mean_df[(column.name, "mean")],
                     bottom=bottom,
                     color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                     edgecolor='k',
                     linewidth=1)
        else:
            axis.bar([0, 1],
                     mean_df[(column.name, "mean")],
                     bottom=bottom,
                     color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                     hatch=column.hatch,
                     edgecolor='w',
                     linewidth=1)
            axis.bar([0, 1],
                     mean_df[(column.name, "mean")],
                     bottom=bottom,
                     color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                     edgecolor='k',
                     fill=False,
                     linewidth=1)

        for idx in [0, 1]:
            axis.errorbar(x=errorbar_x[index][idx],
                          y=bottom[idx] + mean_df[(column.name, 'mean')][idx],
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
    axis.set_xticklabels(['Control', 'Dlx-CKO'], rotation='horizontal')
    axis.spines['top'].set_visible(False)
    axis.spines['right'].set_visible(False)
    axis.tick_params(axis='x', which='both', bottom=False, labelbottom=True)
    axis.set_title(title, loc=titleloc)
    return axis


fig, ax = plt.subplots()
w = 5.51181
fig.set_figwidth(w)
fig.set_dpi(1000)
cap_size = 4
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"
color_dict = {"Control": custom_colors["Dlx-CKO Control"],
              "Dlx-CKO": custom_colors["Dlx-CKO"]}
y_genotype = ['Control', 'Dlx-CKO']

totalGrooming_ax = plt.subplot2grid((2, 3), (0, 0))
initiationsPerMin_ax = plt.subplot2grid((2, 3), (0, 1))
duration_ax = plt.subplot2grid((2, 3), (0, 2))
allTransQuantity_ax = plt.subplot2grid((2, 3), (1, 0))
distributionTransition_ax = plt.subplot2grid((2, 3), (1, 1), colspan=2)

# Total Grooming Time (Fig 3A)
ordered_totalGrooming_columns = ("nonChainGrooming_percentTrial", "chainGrooming_percentTrial")
totalGrooming_orderedColumns = [Column('nonChainGrooming_percentTrial', hatch='//'),
                                Column('chainGrooming_percentTrial', hatch=None)]

grooming_by_type_mean, grooming_by_type_sem = get_mean_sem(trials_with_chains_mean_sem,
                                                           ordered_totalGrooming_columns)
totalGrooming_ax = create_stacked_bar_chart(totalGrooming_ax,
                                            grooming_by_type_mean,
                                            grooming_by_type_sem,
                                            totalGrooming_orderedColumns)
totalGrooming_ax = format_ax(totalGrooming_ax,
                             ylim=[0, 35],
                             yticks=[10, 20, 30],
                             ylabel='time spent (% of trial)',
                             title='grooming quantity')

# legend_elements = [Patch(facecolor='k', edgecolor='w', label='chain'),
#                    Patch(facecolor='k', hatch='//', edgecolor='w', label='non-chain')]
# totalGrooming_ax.legend(handles=legend_elements, loc='upper left')

## Initiations per Minute Grooming (Fig 3B)

ordered_initiationsPerMin_columns = ("bouts_perMin", "chains_perMin")
initiationsPerMin_orderedColumns = [Column('bouts_perMin', hatch='//'),
                                    Column('chains_perMin', hatch=None)]

initiations_mean, initiations_sem = get_mean_sem(trials_with_chains_mean_sem,
                                                 ordered_initiationsPerMin_columns)
initiationsPerMin_ax = create_stacked_bar_chart(initiationsPerMin_ax,
                                                initiations_mean,
                                                initiations_sem,
                                                initiationsPerMin_orderedColumns)

initiationsPerMin_ax = format_ax(initiationsPerMin_ax,
                                 ylim=[0, 6],
                                 yticks=[2, 4, 6],
                                 ylabel='initiations (per min grooming)',
                                 title='grooming frequency')

# Duration (Fig 3C)
ordered_duration_columns = ("nonchain_duration", "chain_duration")
duration_orderedColumns = [Column('nonchain_duration', hatch='//'),
                           Column('chain_duration', hatch=None)]
duration_mean, duration_sem = get_mean_sem(trials_with_chains_mean_sem,
                                           ordered_duration_columns)
duration_ax = create_stacked_bar_chart(duration_ax,
                                       duration_mean,
                                       duration_sem,
                                       duration_orderedColumns)
duration_ax = format_ax(duration_ax,
                        ylim=[0, 360],
                        yticks=[100, 200, 300],
                        ylabel='duration (seconds)',
                        title='uninterrupted grooming')

# Number of transitions (Fig 3D)
ordered_numberTransitions_columns = ("typicalTransitions_perChain", "atypicalTransitions_perChain")
numberTransitions_orderedColumns = [Column("typicalTransitions_perChain", hatch='+'),
                                    Column("atypicalTransitions_perChain", hatch=None)]
numberTransitions_mean, numberTransitions_sem = get_mean_sem(trials_with_chains_mean_sem,
                                                             ordered_numberTransitions_columns)
allTransQuantity_ax = create_stacked_bar_chart(allTransQuantity_ax,
                                               numberTransitions_mean,
                                               numberTransitions_sem,
                                               numberTransitions_orderedColumns)
allTransQuantity_ax = format_ax(allTransQuantity_ax,
                                ylim=[0, 4],
                                yticks=[1, 2, 3],
                                ylabel='grooming phase transitions\n(per chain initiated)',
                                title='chain transition quantity')

# Distribution of atypical transitions (Fig 3E)
ordered_distributionTransitions_columns = ("reverse_percentAtypicalTransitions",
                                           "atypicalEnd_percentAtypicalTransitions",
                                           "skips_percentAtypicalTransitions")
distributionTransitions_orderedColumns = [Column("reverse_percentAtypicalTransitions", hatch="\\"),
                                          Column('atypicalEnd_percentAtypicalTransitions', hatch='.'),
                                          Column("skips_percentAtypicalTransitions", hatch=None)]
distributionTransitions_mean, distributionTransitions_sem = get_mean_sem(trials_with_chains_mean_sem,
                                                                         ordered_distributionTransitions_columns)
distributionTransition_ax = create_stacked_bar_chart(distributionTransition_ax,
                                                     distributionTransitions_mean,
                                                     distributionTransitions_sem,
                                                     distributionTransitions_orderedColumns)
distributionTransition_ax = format_ax(distributionTransition_ax,
                                      ylim=[0, 110],
                                      yticks=[25, 50, 75, 100],
                                      ylabel='proportion of transitions\n(% of atypical transitions)',
                                      title='distribution of atypical transitions',
                                      titleloc='right')

plt.tight_layout()
plt.savefig(f'/Users/Krista/OneDrive - Umich/figures/figures_ai/figure3/fig3_{today_str}.pdf')
plt.close('all')