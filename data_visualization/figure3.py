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

trials_with_chains.insert(trials_with_chains.shape[1], 'totalGrooming_percentTrial',
                          (trials_with_chains['total_time_grooming'] / trials_with_chains['trial_length']) * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'nonChainGrooming_percentTotalGrooming',
                          (trials_with_chains['nonchain_duration'] / trials_with_chains['total_time_grooming']) * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'chainGrooming_percentTotalGrooming',
                          (trials_with_chains['chain_duration'] / trials_with_chains['total_time_grooming']) * 100)

trials_with_chains.insert(trials_with_chains.shape[1], 'chains_perMin',
                          trials_with_chains['num_chains'] / (trials_with_chains['total_time_grooming'] / 60))

trials_with_chains.insert(trials_with_chains.shape[1], 'chainGrooming_percentTrial',
                          (trials_with_chains['chain_duration'] / (trials_with_chains['trial_length']) * 100))

trials_with_chains.insert(trials_with_chains.shape[1], 'nonChainGrooming_percentTrial',
                          (trials_with_chains['nonchain_duration'] / (trials_with_chains['trial_length']) * 100))

trials_with_chains.to_csv(f'/Users/Krista/OneDrive - Umich/figures/grooming_chains_nonchains_{today_str}.csv')
trials_with_chains_mean_sem = trials_with_chains.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])
trials_with_chains_mean_sem_transpose = trials_with_chains_mean_sem.transpose().reset_index()


# Plotting


def get_mean_sem(agg_df):
    mean = agg_df.loc[agg_df['level_1'] == 'mean']
    sem = agg_df.loc[agg_df['level_1'] == 'sem']
    return mean, sem


def format_ax(axis, ylim, yticks, ylabel, xticklabels, yticklabels=None, title=None, titleloc='center'):
    if yticklabels is None:
        yticklabels = yticks

    axis.set_ylim(ylim[0], ylim[1])
    axis.set_yticks(yticks)
    axis.set_yticklabels(yticklabels)
    axis.set_ylabel(ylabel)
    axis.set_xticklabels(xticklabels, rotation='horizontal')
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

totalGrooming_ax = plt.subplot2grid((2, 4), (0, 0), colspan=2)
# nonChainGrooming_ax = plt.subplot2grid((2, 4), (0, 1))
chainInit_ax = plt.subplot2grid((2, 4), (0, 2))
chainDuraion_ax = plt.subplot2grid((2, 4), (0, 3))
allTransQuantity_ax = plt.subplot2grid((2, 4), (1, 0))
atypicalTransQuantity_ax = plt.subplot2grid((2, 4), (1, 1))
abnormalSyntaxType_ax = plt.subplot2grid((2, 4), (1, 2), colspan=2)

# Total Grooming Time (Fig 3A)
totalGrooming_percentTrial = trials_with_chains_mean_sem_transpose.loc[
    trials_with_chains_mean_sem_transpose['level_0'] == 'totalGrooming_percentTrial']
totalGrooming_percentTrial_mean, totalGrooming_percentTrial_sem = get_mean_sem(totalGrooming_percentTrial)

grooming_by_type_mean = trials_with_chains_mean_sem[[("nonChainGrooming_percentTrial", "mean"),
                                                     ("chainGrooming_percentTrial", "mean")]]
grooming_by_type_sem = trials_with_chains_mean_sem[[("nonChainGrooming_percentTrial", "sem"),
                                                    ("chainGrooming_percentTrial", "sem")]]
grooming_by_type_mean = grooming_by_type_mean.reset_index()
grooming_by_type_sem = grooming_by_type_sem.reset_index()

ind = [0, 1]
totalGrooming_ax.bar(ind,
                          grooming_by_type_mean[('nonChainGrooming_percentTrial', 'mean')],
                          color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                          hatch='//',
                          edgecolor='w',
                          linewidth=1)
totalGrooming_ax.bar(ind,
                          grooming_by_type_mean[('nonChainGrooming_percentTrial', 'mean')],
                          color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                          fill=False,
                          edgecolor='k',
                          linewidth=1)
totalGrooming_ax.bar(ind, grooming_by_type_mean[('chainGrooming_percentTrial', 'mean')],
                          bottom=grooming_by_type_mean[('nonChainGrooming_percentTrial', 'mean')],
                          color=[custom_colors['Dlx-CKO Control'], custom_colors['Dlx-CKO']],
                          edgecolor='k',
                          linewidth=1)

totalGrooming_ax.errorbar(x=-0.1,
                          y=grooming_by_type_mean[('nonChainGrooming_percentTrial', 'mean')][0],
                          yerr=grooming_by_type_sem[('nonChainGrooming_percentTrial', 'sem')][0],
                          ecolor='k')
totalGrooming_ax.errorbar(x=0.1,
                          y=grooming_by_type_mean[('nonChainGrooming_percentTrial', 'mean')][0]+grooming_by_type_mean[('chainGrooming_percentTrial', 'mean')][0],
                          yerr=grooming_by_type_sem[('chainGrooming_percentTrial', 'sem')][0],
                          ecolor='k')
totalGrooming_ax.errorbar(x=0.9,
                          y=grooming_by_type_mean[('nonChainGrooming_percentTrial', 'mean')][1],
                          yerr=grooming_by_type_sem[('nonChainGrooming_percentTrial', 'sem')][1],
                          ecolor='k')
totalGrooming_ax.errorbar(x=1.1,
                          y=grooming_by_type_mean[('nonChainGrooming_percentTrial', 'mean')][1]+grooming_by_type_mean[('chainGrooming_percentTrial', 'mean')][1],
                          yerr=grooming_by_type_sem[('chainGrooming_percentTrial', 'sem')][1],
                          ecolor='k')
totalGrooming_ax.set_xticks([0, 1])
totalGrooming_ax = format_ax(totalGrooming_ax,
                             ylim=[0, 35],
                             yticks=[10, 20, 30],
                             ylabel='time spent\n(% of trial)',
                             xticklabels=['Control', 'Dlx-CKO'],
                             title='Grooming quantity',
                             titleloc='center')
legend_elements = [Patch(facecolor='k', edgecolor='w', label='chain'),
                   Patch(facecolor='k', hatch='//', edgecolor='w', label = 'non-chain')]
totalGrooming_ax.legend(handles=legend_elements, loc='upper left')

# # Non-Chain Grooming (Fig 3B)
# nonChainGrooming_percentTotal = trials_with_chains_mean_sem_transpose.loc[
#     trials_with_chains_mean_sem_transpose['level_0'] == 'nonChainGrooming_percentTotalGrooming']
# nonChainGrooming_percentTotal_mean, nonChainGrooming_percentTotal_sem = get_mean_sem(nonChainGrooming_percentTotal)
#
# nonChainGrooming_percentTotal_mean.plot.bar(ax=nonChainGrooming_ax,
#                                             y=y_genotype,
#                                             color=color_dict,
#                                             yerr=[nonChainGrooming_percentTotal_sem['Control'],
#                                                   nonChainGrooming_percentTotal_sem['Dlx-CKO']],
#                                             capsize=cap_size,
#                                             legend=False)
#
# # line_y = [mean_time_grooming_session['ko_mean'].item() + sem_time_grooming_session['ko_sem'].item() + 75] * 2
# # line_x = [-0.125, 0.125]
# #
# # totalGrooming_ax.plot(line_x, line_y, color='black', linewidth=1.0)
# # totalGrooming_ax.annotate('*', xy=(0, 835), xycoords='data', ha='center')
#
# nonChainGrooming_ax = format_ax(nonChainGrooming_ax,
#                                 ylim=[0, 100],
#                                 yticks=[25, 50, 75, 100],
#                                 ylabel='time spent\n(% of total grooming)',
#                                 xticklabels=['non-chain'])

# Chains Initiated per Minute Grooming (Fig 3C)
chains_perMin = trials_with_chains_mean_sem_transpose.loc[
    trials_with_chains_mean_sem_transpose['level_0'] == 'chains_perMin']
chains_perMin_mean, chains_perMin_sem = get_mean_sem(chains_perMin)

chains_perMin_mean.plot.bar(ax=chainInit_ax,
                            y=y_genotype,
                            color=color_dict,
                            yerr=[chains_perMin_sem['Control'], chains_perMin_sem['Dlx-CKO']],
                            capsize=cap_size,
                            legend=False)

# line_y = [mean_num_bouts_plot_df['ko_mean'].item() + sem_num_bouts_plot_df['ko_sem'].item() + 2] * 2
# line_x = [-0.125, 0.125]

chainInit_ax = format_ax(chainInit_ax,
                         ylim=[0, 1.6],
                         yticks=[0.5, 1, 1.5],
                         ylabel='chain initiation\n(per min grooming)',
                         xticklabels=['chains'])

# Chain Duration
chain_duration = chains_mean_sem_transpose.loc[chains_mean_sem_transpose['level_0'] == 'duration_seconds']
chain_duration_mean, chain_duration_sem = get_mean_sem(chain_duration)

chain_duration_mean.plot.bar(ax=chainDuraion_ax,
                             y=['Control', 'Dlx-CKO'],
                             color={"Control": custom_colors["Dlx-CKO Control"], "Dlx-CKO": custom_colors["Dlx-CKO"]},
                             yerr=[chain_duration_sem['Control'], chain_duration_sem['Dlx-CKO']],
                             capsize=cap_size,
                             legend=False)

## Statistical significance line
# line_y = [chain_duration_mean['Dlx-CKO Control'].item() + chain_duration_sem['Dlx-CKO Control'].item() + 2] * 2
# line_x = [-0.125, 0.125]
#
# chainDuraion_ax.plot(line_x, line_y, color='black', linewidth=1.0)
# chainDuraion_ax.annotate('*',
#                       xy=(
#              0, np.round(chain_duration_mean['Dlx-CKO Control'].item() + chain_duration_sem['Dlx-CKO Control'].item() + 2 + 2)),
#                       xycoords='data',
#                       ha='center')

chainDuraion_ax.set_ylim(0, 12)
chainDuraion_ax.set_yticks([4, 6, 8, 12])
chainDuraion_ax.set_yticklabels([4, 6, 8, 12])
chainDuraion_ax.set_ylabel('seconds (per chain)')
chainDuraion_ax.set_xticklabels(['chain duration'], rotation='horizontal')
chainDuraion_ax.spines['top'].set_visible(False)
chainDuraion_ax.spines['right'].set_visible(False)
chainDuraion_ax.tick_params(axis='x', which='both', bottom=False)

# Total number of transitions per chain

numTrans_perChain = chains_mean_sem_transpose.loc[chains_mean_sem_transpose['level_0'] == 'num_transitions']
numTrans_perChain_mean, numTrans_perChain_sem = get_mean_sem(numTrans_perChain)

numTrans_perChain_mean.plot.bar(ax=allTransQuantity_ax,
                                y=['Control', 'Dlx-CKO'],
                                color={"Control": custom_colors["Dlx-CKO Control"],
                                       "Dlx-CKO": custom_colors["Dlx-CKO"]},
                                yerr=[numTrans_perChain_sem['Control'], numTrans_perChain_sem['Dlx-CKO']],
                                capsize=cap_size,
                                legend=False
                                )

allTransQuantity_ax.set_ylim(0, 4.25)
allTransQuantity_ax.set_yticks([1, 2, 3, 4])
allTransQuantity_ax.set_yticklabels([1, 2, 3, 4])
allTransQuantity_ax.set_ylabel('number (per chain)')
allTransQuantity_ax.set_xticklabels(['# transitions'], rotation='horizontal')
allTransQuantity_ax.spines['top'].set_visible(False)
allTransQuantity_ax.spines['right'].set_visible(False)
allTransQuantity_ax.tick_params(axis='x', which='both', bottom=False)

# Atypical transitions as a proportion of total transitions

proportionAtypicalTrans_perChain = chains_mean_sem_transpose.loc[
    chains_mean_sem_transpose['level_0'] == 'proportion_atypicalTransitions']
proportionAtypicalTrans_perChain_mean, proportionAtypicalTrans_perChain_sem = get_mean_sem(
    proportionAtypicalTrans_perChain)

proportionAtypicalTrans_perChain_mean.plot.bar(ax=atypicalTransQuantity_ax,
                                               y=['Control', 'Dlx-CKO'],
                                               color={"Control": custom_colors["Dlx-CKO Control"],
                                                      "Dlx-CKO": custom_colors["Dlx-CKO"]},
                                               yerr=[proportionAtypicalTrans_perChain_sem['Control'],
                                                     proportionAtypicalTrans_perChain_sem['Dlx-CKO']],
                                               capsize=cap_size,
                                               legend=False)

## significance bars
# total_transitions_yoffset = mean_total_transitions_bout[
#                                 mean_total_transitions_bout.measure
#                                 == 'total_transitions']['ctrl_mean'].item() \
#                             + sem_total_transitions_bout[
#                                 sem_total_transitions_bout.measure
#                                 == 'total_transitions']['ctrl_sem'].item() \
#                             + 0.5
# incorrect_transitions_yoffset = mean_total_transitions_bout[
#                                     mean_total_transitions_bout.measure
#                                     == 'total_incorrect_transitions']['ctrl_mean'].item() \
#                                 + sem_total_transitions_bout[
#                                     sem_total_transitions_bout.measure
#                                     == 'total_incorrect_transitions']['ctrl_sem'].item() \
#                                 + 0.5
#
# line_x_total_transitions = [-0.125, 0.125]
# line_y_total_transitions = [total_transitions_yoffset] * 2
#
# line_x_incorrect_transitions = [0.875, 1.125]
# line_y_incorrect_transitions = [incorrect_transitions_yoffset] * 2
#
# atypicalTransQuantity_ax.plot(line_x_total_transitions, line_y_total_transitions, color='black', linewidth=1.0)
# atypicalTransQuantity_ax.annotate('*',
#              xy=(0, total_transitions_yoffset),
#              xycoords='data',
#              ha='center')
#
# atypical_transitions_totalplot(line_x_incorrect_transitions, line_y_incorrect_transitions, color='black', linewidth=1.0)
# atypicalTransQuantity_ax.annotate('*',
#              xy=(1, incorrect_transitions_yoffset),
#              xycoords='data',
#              ha='center')

atypicalTransQuantity_ax.set_ylim(0, 0.6)
atypicalTransQuantity_ax.set_yticks([0.2, 0.4, 0.6])
atypicalTransQuantity_ax.set_yticklabels([20, 40, 60])
atypicalTransQuantity_ax.set_xticklabels(['# transitions'], rotation='horizontal')
atypicalTransQuantity_ax.set_ylabel('atypical transitions\n(% of total transitions)')
atypicalTransQuantity_ax.spines['top'].set_visible(False)
atypicalTransQuantity_ax.spines['right'].set_visible(False)
atypicalTransQuantity_ax.tick_params(axis='x', which='both', bottom=False)

## Proportion Atypical Transitions Per Chain
atypical_transitions = ['proportion_skips',
                        'proportion_reverse',
                        'proportion_atypical_end']
proportionSkips = chains_mean_sem_transpose.loc[chains_mean_sem_transpose['level_0'] == 'proportion_skips']
proportionReverse = chains_mean_sem_transpose.loc[chains_mean_sem_transpose['level_0'] == 'proportion_reverse']
proportionAtypEnd = chains_mean_sem_transpose.loc[chains_mean_sem_transpose['level_0'] == 'proportion_atypical_end']
atypicalTrans_segmented = pd.concat([proportionSkips, proportionReverse, proportionAtypEnd])
atypicalTrans_segmented_mean, atypicalTrans_segmented_sem = get_mean_sem(atypicalTrans_segmented)

mapping = {transition: i for i, transition in enumerate(atypical_transitions)}
mean_key = atypicalTrans_segmented_mean.level_0.map(mapping)
mean_atypicalTrans_segmented_sorted = atypicalTrans_segmented_mean.iloc[mean_key.argsort()]
sem_key = atypicalTrans_segmented_sem.level_0.map(mapping)
sem_atypicalTrans_segmented_sorted = atypicalTrans_segmented_sem.iloc[sem_key.argsort()]

mean_atypicalTrans_segmented_sorted.plot.bar(ax=abnormalSyntaxType_ax,
                                             x='level_0',
                                             y=y_genotype,
                                             color=color_dict,
                                             yerr=[sem_atypicalTrans_segmented_sorted['Control'].to_list(),
                                                   sem_atypicalTrans_segmented_sorted['Dlx-CKO'].to_list()],
                                             capsize=cap_size)

## significance bars
# incorrect_initiation_yoffset = mean_sem_atypical_transistions_sorted[
#                                    mean_sem_atypical_transistions_sorted.measure
#                                    == 'prop_initiation_incorrect_transitions']['ko_mean'].item() \
#                                + sem_incorrect_transitions_prop_session[
#                                    sem_incorrect_transitions_prop_session.measure
#                                    == 'prop_initiation_incorrect_transitions']['ko_sem'].item() \
#                                + 0.05
# skipped_yoffset = mean_sem_atypical_transistions_sorted[
#                       mean_sem_atypical_transistions_sorted.measure
#                       == 'prop_skipped_transitions']['ctrl_mean'].item() \
#                   + sem_incorrect_transitions_prop_session[
#                       sem_incorrect_transitions_prop_session.measure
#                       == 'prop_skipped_transitions']['ctrl_sem'].item() \
#                   + 0.05
# reversed_yoffset = mean_sem_atypical_transistions_sorted[
#                        mean_sem_atypical_transistions_sorted.measure
#                        == 'prop_reversed_transitions']['ctrl_mean'].item() \
#                    + sem_incorrect_transitions_prop_session[
#                        sem_incorrect_transitions_prop_session.measure
#                        == 'prop_reversed_transitions']['ctrl_sem'].item() \
#                    + 0.05
# aborted_yoffset = mean_sem_atypical_transistions_sorted[
#                       mean_sem_atypical_transistions_sorted.measure
#                       == 'prop_aborted_transitions']['ko_mean'].item() \
#                   + sem_incorrect_transitions_prop_session[
#                       sem_incorrect_transitions_prop_session.measure
#                       == 'prop_aborted_transitions']['ko_sem'].item() \
#                   + 0.05
#
#
# line_y_incorrect_initiation = [incorrect_initiation_yoffset] * 2
# line_x_incorrect_initiation = [-0.125, 0.125]
#
# line_y_skipped = [skipped_yoffset] * 2
# line_x_skipped = [0.875, 1.125]
#
# line_y_reversed = [reversed_yoffset] * 2
# line_x_reversed = [1.875, 2.125]
#
# line_y_aborted = [aborted_yoffset] * 2
# line_x_aborted = [2.875, 3.125]
#
# ax4.plot(line_x_incorrect_initiation, line_y_incorrect_initiation, color='black', linewidth=1.0)
# ax4.annotate('*',
#              xy=(0, incorrect_initiation_yoffset),
#              xycoords='data',
#              ha='center')
#
# ax4.plot(line_x_skipped, line_y_skipped, color='black', linewidth=1.0)
# ax4.annotate('*',
#              xy=(1, skipped_yoffset),
#              xycoords='data',
#              ha='center')
#
# ax4.plot(line_x_reversed, line_y_reversed, color='black', linewidth=1.0)
# ax4.annotate('*',
#              xy=(2, reversed_yoffset),
#              xycoords='data',
#              ha='center')
#
# ax4.plot(line_x_aborted, line_y_aborted, color='black', linewidth=1.0)
# ax4.annotate('*',
#              xy=(3, aborted_yoffset),
#              xycoords='data',
#              ha='center')

abnormalSyntaxType_ax = format_ax(abnormalSyntaxType_ax,
                                  ylim=[0, 0.8],
                                  yticks=[0.25, 0.5, 0.75],
                                  ylabel='proportion of transitions\n(% of atypical transitions)',
                                  xticklabels=['skip', 'reverse', 'atypical end'],
                                  yticklabels=[25, 50, 75],
                                  title='Distribution of atypical transitions',
                                  titleloc='left')

handles, _ = abnormalSyntaxType_ax.get_legend_handles_labels()
labels = ['control', 'Dlx-CKO']
abnormalSyntaxType_ax.legend(handles, labels)
abnormalSyntaxType_ax.set_xlabel(None)
abnormalSyntaxType_ax.get_legend().set_title(None)

plt.tight_layout()
plt.savefig(f'/Users/Krista/OneDrive - Umich/figures/figures_ai/figure3/fig3_{today_str}.pdf')
plt.close('all')