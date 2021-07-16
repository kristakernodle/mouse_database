import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

import database_pkg as dbpkg
from data_visualization.plot_functions import get_mean_sem, genotype_cleanup, Column, create_stacked_bar_chart, \
    format_ax

custom_colors = {'Dlx-CKO Control': "#005AB5", "Dlx-CKO": "#DC3220"}
experiment = dbpkg.Experiment.get_by_name("dlxCKO-pasta-handling")

phScores_df = pd.read_sql(dbpkg.db.session.query(dbpkg.Mouse.mouse_id,
                                                 dbpkg.Mouse.eartag,
                                                 dbpkg.Mouse.sex,
                                                 dbpkg.Mouse.birthdate,
                                                 dbpkg.Mouse.genotype,
                                                 dbpkg.Session.session_id,
                                                 dbpkg.Session.session_date,
                                                 dbpkg.Session.session_dir,
                                                 dbpkg.Session.session_num,
                                                 dbpkg.PastaHandlingScores.pasta_handling_score_id,
                                                 dbpkg.PastaHandlingScores.trial_num,
                                                 dbpkg.PastaHandlingScores.time_to_eat,
                                                 dbpkg.PastaHandlingScores.left_forepaw_adjustments,
                                                 dbpkg.PastaHandlingScores.right_forepaw_adjustments,
                                                 dbpkg.PastaHandlingScores.left_forepaw_failure_to_contact,
                                                 dbpkg.PastaHandlingScores.right_forepaw_failure_to_contact,
                                                 dbpkg.PastaHandlingScores.guide_grasp_switch,
                                                 dbpkg.PastaHandlingScores.drops,
                                                 dbpkg.PastaHandlingScores.mouth_pulling,
                                                 dbpkg.PastaHandlingScores.pasta_long_paws_together,
                                                 dbpkg.PastaHandlingScores.pasta_short_paws_apart,
                                                 dbpkg.PastaHandlingScores.abnormal_posture,
                                                 dbpkg.PastaHandlingScores.iron_grip,
                                                 dbpkg.PastaHandlingScores.guide_around_grasp,
                                                 dbpkg.PastaHandlingScores.angling_with_head_tilt) \
                          .join(dbpkg.Session, dbpkg.Session.mouse_id == dbpkg.Mouse.mouse_id) \
                          .join(dbpkg.PastaHandlingScores,
                                dbpkg.PastaHandlingScores.session_id == dbpkg.Session.session_id) \
                          .statement,
                          dbpkg.db.session.bind)

phScores_df.insert(phScores_df.shape[1], 'forepaw_adjustments',
                   (phScores_df['left_forepaw_adjustments'] +
                    phScores_df['right_forepaw_adjustments']))

phScores_df.insert(phScores_df.shape[1], 'forepaw_failure_to_contact',
                   (phScores_df['left_forepaw_failure_to_contact'] +
                    phScores_df['right_forepaw_failure_to_contact']))

phScores_df.to_csv('/Users/Krista/OneDrive - Umich/figures/pastaHandling_20210708.csv')

phScores_trialAgg_df = phScores_df.groupby("genotype").agg([pd.DataFrame.mean, pd.DataFrame.sem])

# phScores_trialAgg_df = phScores_trialAgg_df.transpose().reset_index()
# out = phScores_trialAgg_df.rename(
#     columns={"level_0": 'measure', 'level_1': "statistic", 'Control': "control", 'Knock-Out': 'Dlx-CKO'})

## Start Figures

# Figure level settings
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"

fig, ax = plt.subplots()
fig.set_figwidth(7.48031)
fig.set_figheight(2.5)
fig.set_dpi(1000)

# forepawAdjustment_ax = plt.subplot2grid((1, 6), (0, 0))
atypicalBehavior_ax = plt.subplot2grid((1, 6), (0, 0), colspan=6)

bar_width = 0.35

columns_dict = {atypicalBehavior_ax: [Column('forepaw_failure_to_contact', label='any forepaw\nno contact'),
                                      Column('pasta_long_paws_together', label="pasta long,\npaws together"),
                                      Column('pasta_short_paws_apart', label="pasta short,\npaws apart"),
                                      Column('guide_grasp_switch', label="guide/grasp\nswitch"),
                                      Column('mouth_pulling', label="mouth\npulling"),
                                      Column('drops', label="drops")]}
                #                       forepawAdjustment_ax: [Column('forepaw_adjustments', label=None)]

# forepawAdjustment_orderedColumns = columns_dict[forepawAdjustment_ax]
# forepawAdjustment_mean, forepawAdjustment_sem = get_mean_sem(phScores_trialAgg_df,
#                                                              forepawAdjustment_orderedColumns)
# forepawAdjustment_mean = forepawAdjustment_mean.set_index(('genotype',)).transpose().reset_index().set_index('level_0')
# forepawAdjustment_sem = forepawAdjustment_sem.set_index(('genotype',)).transpose().reset_index().set_index('level_0')

# forepawAdjustment_x = list(range(len(forepawAdjustment_mean)))

# forepawAdjustment_ax.bar([xval - bar_width / 2 for xval in forepawAdjustment_x],
#                          forepawAdjustment_mean['Dlx-CKO Control'],
#                          bar_width=bar_width,
#                          color=custom_colors['Dlx-CKO Control'],
#                          label='control')
# forepawAdjustment_ax.bar([xval + bar_width / 2 for xval in forepawAdjustment_x],
#                          forepawAdjustment_mean['Dlx-CKO'],
#                          bar_width=bar_width,
#                          color=custom_colors['Dlx-CKO'],
#                          label='Dlx-CKO')
#
# forepawAdjustment_ax.errorbar(x=[xval - bar_width / 2 for xval in forepawAdjustment_x],
#                               y=forepawAdjustment_mean['Dlx-CKO Control'],
#                               yerr=forepawAdjustment_sem['Dlx-CKO Control'],
#                               ecolor='k',
#                               capsize=2,
#                               ls='none')
# forepawAdjustment_ax.errorbar(x=[xval + bar_width / 2 for xval in forepawAdjustment_x],
#                               y=forepawAdjustment_mean['Dlx-CKO'],
#                               yerr=forepawAdjustment_sem['Dlx-CKO'],
#                               ecolor='k',
#                               capsize=2,
#                               ls='none')
#
# forepawAdjustment_ax.set_xticks([0])
# forepawAdjustment_ax.set_xticklabels(["forepaw\nadjustments"],
#                                     fontsize=9)
# forepawAdjustment_ax.set_yticks([50, 100, 150])
# forepawAdjustment_ax.set_yticklabels([50, 100, 150])
# forepawAdjustment_ax.set_ylabel("number of forepaw adjustments\n(per trial)")
# forepawAdjustment_ax.tick_params(axis='x', bottom=False)
# forepawAdjustment_ax.spines['top'].set_visible(False)
# forepawAdjustment_ax.spines['right'].set_visible(False)
# forepawAdjustment_ax = format_ax(forepawAdjustment_ax,)

# atypical behaviors
atypicalBehaviors_orderedColumns = columns_dict[atypicalBehavior_ax]
atypicalBehaviors_mean, atypicalBehaviors_sem = get_mean_sem(phScores_trialAgg_df,
                                                             atypicalBehaviors_orderedColumns)

atypicalBehaviors_mean = atypicalBehaviors_mean.set_index(('genotype',)).transpose().reset_index().set_index('level_0')
atypicalBehaviors_sem = atypicalBehaviors_sem.set_index(('genotype',)).transpose().reset_index().set_index('level_0')

atypicalBehavior_x = list(range(len(atypicalBehaviors_mean)))

atypicalBehavior_ax.bar([xval - bar_width / 2 for xval in atypicalBehavior_x],
                        atypicalBehaviors_mean['Dlx-CKO Control'],
                        width=bar_width,
                        color=custom_colors['Dlx-CKO Control'],
                        label='control')
atypicalBehavior_ax.bar([xval + bar_width / 2 for xval in atypicalBehavior_x],
                        atypicalBehaviors_mean['Dlx-CKO'],
                        width=bar_width,
                        color=custom_colors['Dlx-CKO'],
                        label='Dlx-CKO')

atypicalBehavior_ax.errorbar(x=[xval - bar_width / 2 for xval in atypicalBehavior_x],
                             y=atypicalBehaviors_mean['Dlx-CKO Control'],
                             yerr=atypicalBehaviors_sem['Dlx-CKO Control'],
                             ecolor='k',
                             capsize=2,
                             ls='none')
atypicalBehavior_ax.errorbar(x=[xval + bar_width / 2 for xval in atypicalBehavior_x],
                             y=atypicalBehaviors_mean['Dlx-CKO'],
                             yerr=atypicalBehaviors_sem['Dlx-CKO'],
                             ecolor='k',
                             capsize=2,
                             ls='none')

atypicalBehavior_ax.set_xticks(atypicalBehavior_x)
atypicalBehavior_ax.set_xticklabels([column.label for column in atypicalBehaviors_orderedColumns],
                                    fontsize=9)
atypicalBehavior_ax.set_xlabel(None)
atypicalBehavior_ax.set_ylabel('# times performed\n(events per trial)')
atypicalBehavior_ax.set_ylim(0, 1.9)
atypicalBehavior_ax.set_yticks([0.5, 1, 1.5])
atypicalBehavior_ax.set_yticklabels([0.5, 1, 1.5])
atypicalBehavior_ax.legend(title=None, labels=["control", "Dlx-CKO"])
atypicalBehavior_ax.tick_params(axis='x', bottom=False)

ctrl_x = [xval - bar_width / 2 for xval in atypicalBehavior_x]
ko_x = [xval + bar_width / 2 for xval in atypicalBehavior_x]
drops_x = [ctrl_x[-1], ko_x[-1]]

atypicalBehavior_ax.plot(drops_x, [1.75, 1.75], color='black', linewidth=1.0)
atypicalBehavior_ax.annotate('*',
                             xy=(sum(drops_x)/2, 1.75),
                             xycoords='data',
                             ha='center')
atypicalBehavior_ax.spines['top'].set_visible(False)
atypicalBehavior_ax.spines['right'].set_visible(False)
plt.tight_layout(pad=0.2)
plt.savefig('/Users/Krista/OneDrive - Umich/figures/figures_ai/figure2/fig2_20210715.pdf')
plt.close('all')
