import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

from database_pkg import Mouse, Experiment, Session, SRTrialScore, Trial, Reviewer


def remove_duplicate_scored_trials(scored_trials):
    duplicate_trial_dirs = scored_trials[scored_trials.duplicated(['trial_dir'])]['trial_dir']
    for dup_trial_dir in duplicate_trial_dirs:
        dup_trials = scored_trials.loc[scored_trials.trial_dir == dup_trial_dir]

        if len(dup_trials) < 2:
            break

        for name in ['Krista K', 'Alli C', 'Alli B', 'Jen M', 'Dan L']:
            if name in dup_trials.reviewer.to_list():
                scored_trials.drop(dup_trials.loc[dup_trials.reviewer != name].index.to_list())
                break
    return scored_trials


def convert_reach_scores_df_proportion_df(genotype_reach_scores):
    proportion_list = list()
    for index, row in genotype_reach_scores.iterrows():
        row_dict = {'eartag': row.eartag,
                    'genotype': row.genotype,
                    'birthdate': row.birthdate,
                    'sex': row.sex,
                    'session_num': row.session_num}

        proportions = {'contact miss': row.pellet_removed,
                       'no contact miss': row.pellet_remains}

        for key in proportions.keys():
            this_row = dict(**row_dict,
                            **{'miss_type': key,
                               'value': proportions[key]}
                            )
            proportion_list.append(this_row)
    return pd.DataFrame.from_records(proportion_list)


experiment = Experiment.get_by_name('dlxCKO-skilled-reaching')

all_scored_trials = experiment.get_all_scored_trials()
all_scored_trials = remove_duplicate_scored_trials(all_scored_trials)

participated_scored_trials = all_scored_trials.loc[(all_scored_trials['reach_score'].isin([1, 2, 3, 4, 5, 6, 8, 9]))]



trials_per_mouse_per_session = participated_scored_trials.groupby(
    ["session_dir", "session_num", "genotype"]).size().reset_index()
trials_per_mouse_per_session = trials_per_mouse_per_session.rename(columns={0: 'num_trials'})
sessions_less_than_20_reaches = trials_per_mouse_per_session.loc[trials_per_mouse_per_session['num_trials'] < 20]

removed_sessions = list()
for idx, [session_dir, _, _, num_trials] in sessions_less_than_20_reaches.iterrows():
    session = Session.query.filter_by(experiment_id=experiment.experiment_id, session_dir=session_dir).first()
    mouse = Mouse.query.get(session.mouse_id)

    if 'Control' in mouse.genotype:
        genotype = 'Control'
    else:
        genotype = 'Knock-Out'

    removed_sessions.append(
        {
            'eartag': mouse.eartag,
            'genotype': genotype,
            'birthdate': mouse.birthdate,
            'sex': mouse.sex,
            'session_num': session.session_num,
            'session_date': session.session_date,
            'session_dir': session.session_dir,
            'num_trials': num_trials
        }
    )

trials_for_analysis = participated_scored_trials.loc[
    ~participated_scored_trials['session_dir'].isin(sessions_less_than_20_reaches['session_dir'].to_list())]

abnormal_movt_by_session_dir = trials_for_analysis.groupby(trials_for_analysis.session_dir)['abnormal_movt_score'] \
    .value_counts() \
    .unstack() \
    .fillna(0)

abnormal_movt_by_eartag_by_session_list_dict = list()
for session_dir, abnormal_movt_count in abnormal_movt_by_session_dir.iterrows():
    session = Session.query.filter_by(experiment_id=experiment.experiment_id, session_dir=session_dir).first()
    mouse = Mouse.query.get(session.mouse_id)

    if 'Control' in mouse.genotype:
        genotype = 'Control'
    else:
        genotype = 'Knock-Out'

    abnormal_movt_by_eartag_by_session_list_dict.append(
        {'eartag': mouse.eartag,
         'genotype': genotype,
         'birthdate': mouse.birthdate,
         'sex': mouse.sex,
         'session_num': session.session_num,
         'session_date': session.session_date,
         'session_dir': session.session_dir,
         'abnormal_movt_count': abnormal_movt_count[True],
         'percent_ab_movt': abnormal_movt_count[True] / (abnormal_movt_count[True] + abnormal_movt_count[False])})

abnormal_movt_by_session_df = pd.DataFrame.from_records(abnormal_movt_by_eartag_by_session_list_dict)

reach_scores_by_session_dir = trials_for_analysis.groupby(trials_for_analysis.session_dir)['reach_score'] \
    .value_counts() \
    .unstack() \
    .fillna(0)

reach_scores_by_eartag_by_session_list_dict = list()
for session_dir, all_reach_score_counts in reach_scores_by_session_dir.iterrows():
    session = Session.query.filter_by(experiment_id=experiment.experiment_id, session_dir=session_dir).first()
    mouse = Mouse.query.get(session.mouse_id)

    if 'Control' in mouse.genotype:
        genotype = 'Control'
    else:
        genotype = 'Knock-Out'

    total_trials = sum([all_reach_score_counts[i] for i in [1, 2, 3, 4, 5, 6, 8, 9]])
    failure_trials = sum([all_reach_score_counts[i] for i in [3, 4, 5, 6, 8, 9]])

    reach_scores_by_eartag_by_session_list_dict.append(
        {
            'eartag': mouse.eartag,
            'genotype': genotype,
            'birthdate': mouse.birthdate,
            'sex': mouse.sex,
            'session_num': session.session_num,
            'session_date': session.session_date,
            'session_dir': session.session_dir,
            '1': all_reach_score_counts[1],
            '2': all_reach_score_counts[2],
            '3': all_reach_score_counts[3],
            '4': all_reach_score_counts[4],
            '5': all_reach_score_counts[5],
            '6': all_reach_score_counts[6],
            '8': all_reach_score_counts[8],
            '9': all_reach_score_counts[9],
            'total_trials': total_trials,
            'first_success': all_reach_score_counts[1] / total_trials,
            'any_success': (all_reach_score_counts[1] + all_reach_score_counts[2]) / total_trials,
            'pellet_remains': all_reach_score_counts[5] / total_trials,
            'pellet_removed': all_reach_score_counts[4] / total_trials,
            'failure_rate_score_4': all_reach_score_counts[4] / failure_trials,
            'failure_rate_score_5': all_reach_score_counts[5] / failure_trials
        }
    )

reach_scores_by_eartag_by_session_df = pd.DataFrame.from_records(reach_scores_by_eartag_by_session_list_dict)

# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "total_trials",
#                                             reach_scores_by_eartag_by_session_df.iloc[:, 7:].count(axis=1))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "viable_trials",
#                                             reach_scores_by_eartag_by_session_df.iloc[:,
#                                             [8, 9, 10, 11, 12]].sum(axis=1))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "successful_trials",
#                                             reach_scores_by_eartag_by_session_df.iloc[:, [8, 9]].sum(axis=1))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "unsuccessful_trials",
#                                             reach_scores_by_eartag_by_session_df.iloc[:, [10, 11, 12]].sum(axis=1))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "first_success",
#                                             reach_scores_by_eartag_by_session_df['1'] *
#                                             100 / reach_scores_by_eartag_by_session_df['viable_trials'])
# reach_scores_by_eartag_by_session_df['first_success'] = reach_scores_by_eartag_by_session_df[
#     'first_success'].fillna(0)
#
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "any_success",
#                                             (reach_scores_by_eartag_by_session_df['1'] +
#                                              reach_scores_by_eartag_by_session_df['2']) * 100 /
#                                             reach_scores_by_eartag_by_session_df['viable_trials'])

# reach_scores_by_eartag_by_session_df['any_success'] = reach_scores_by_eartag_by_session_df['any_success'].fillna(0)

# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_1', (
#         reach_scores_by_eartag_by_session_df['1'] / reach_scores_by_eartag_by_session_df['viable_trials']))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_1_s', (
#         reach_scores_by_eartag_by_session_df['1'] / reach_scores_by_eartag_by_session_df['successful_trials']))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_2', (
#         reach_scores_by_eartag_by_session_df['2'] / reach_scores_by_eartag_by_session_df['viable_trials']))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_2_s', (
#         reach_scores_by_eartag_by_session_df['2'] / reach_scores_by_eartag_by_session_df['successful_trials']))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_3', (
#         reach_scores_by_eartag_by_session_df['3'] / reach_scores_by_eartag_by_session_df['viable_trials']))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_3_s', (
#         reach_scores_by_eartag_by_session_df['3'] / reach_scores_by_eartag_by_session_df['unsuccessful_trials']))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_4', (
#         reach_scores_by_eartag_by_session_df['4'] / reach_scores_by_eartag_by_session_df['viable_trials']))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_4_s', (
#         reach_scores_by_eartag_by_session_df['4'] / reach_scores_by_eartag_by_session_df['unsuccessful_trials']))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_5', (
#         reach_scores_by_eartag_by_session_df['5'] / reach_scores_by_eartag_by_session_df['viable_trials']))
# reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_5_s', (
#         reach_scores_by_eartag_by_session_df['5'] / reach_scores_by_eartag_by_session_df['unsuccessful_trials']))
#
# reach_scores_by_eartag_by_session_df['prop_1'] = reach_scores_by_eartag_by_session_df['prop_1'].fillna(0)
# reach_scores_by_eartag_by_session_df['prop_1_s'] = reach_scores_by_eartag_by_session_df['prop_1_s'].fillna(0)
# reach_scores_by_eartag_by_session_df['prop_2'] = reach_scores_by_eartag_by_session_df['prop_2'].fillna(0)
# reach_scores_by_eartag_by_session_df['prop_2_s'] = reach_scores_by_eartag_by_session_df['prop_2_s'].fillna(0)
# reach_scores_by_eartag_by_session_df['prop_3'] = reach_scores_by_eartag_by_session_df['prop_3'].fillna(0)
# reach_scores_by_eartag_by_session_df['prop_3_s'] = reach_scores_by_eartag_by_session_df['prop_3_s'].fillna(0)
# reach_scores_by_eartag_by_session_df['prop_4'] = reach_scores_by_eartag_by_session_df['prop_4'].fillna(0)
# reach_scores_by_eartag_by_session_df['prop_4_s'] = reach_scores_by_eartag_by_session_df['prop_4_s'].fillna(0)
# reach_scores_by_eartag_by_session_df['prop_5'] = reach_scores_by_eartag_by_session_df['prop_5'].fillna(0)
# reach_scores_by_eartag_by_session_df['prop_5_s'] = reach_scores_by_eartag_by_session_df['prop_5_s'].fillna(0)

trials_per_mouse_per_session_list = list()
for idx, [session_dir, session_num, genotype, num_trials] in trials_per_mouse_per_session.iterrows():
    session = Session.query.filter_by(experiment_id=experiment.experiment_id, session_dir=session_dir).first()
    mouse = Mouse.query.get(session.mouse_id)

    if 'Control' in mouse.genotype:
        genotype = 'Control'
    else:
        genotype = 'Knock-Out'

    trials_per_mouse_per_session_list.append(
        {
            'eartag': mouse.eartag,
            'genotype': genotype,
            'birthdate': mouse.birthdate,
            'sex': mouse.sex,
            'session_num': session.session_num,
            'session_date': session.session_date,
            'session_dir': session.session_dir,
            'total_trials': num_trials,
        }
    )

trials_per_mouse_per_session = pd.DataFrame.from_records(trials_per_mouse_per_session_list)

trials_per_mouse_per_session.to_csv("/Users/Krista/Desktop/figures/trials_per_mouse_per_session_20220130_corrected.csv")

reach_scores_by_eartag_by_session_df.to_csv(
    "/Users/Krista/Desktop/figures/reach_scores_by_eartag_by_session_df_20220130_corrected.csv")

ctrl_reach_scores = reach_scores_by_eartag_by_session_df[reach_scores_by_eartag_by_session_df['genotype'] == 'Control']
ko_reach_scores = reach_scores_by_eartag_by_session_df[reach_scores_by_eartag_by_session_df['genotype'] == 'Knock-Out']

ctrl_proportion_df = convert_reach_scores_df_proportion_df(ctrl_reach_scores)
ko_proportion_df = convert_reach_scores_df_proportion_df(ko_reach_scores)

## Start Figures

# Figure level settings
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"
plt.rcParams['xtick.major.pad'] = -0.5
plt.rcParams['ytick.major.pad'] = -0.5

cap_size = 4
cap_thick = 1.5
err_line_width = 1.5
line_width = 1.5
dashed_lines = (2, 1)
any_success_linespacing = 0.25

sns.set_theme(context='paper', style="white")
figure = plt.figure()
w = 7.48031
figure.set_figwidth(w)
figure.set_dpi(1000)
# figure.subplots_adjust(bottom=0.025, left=0.025, top=0.975, right=0.975)

genotype_palette = {"Control": "#005AB5", "Knock-Out": "#DC3220"}

# Define axes
total_trials_ax = plt.subplot2grid((3, 2), (0, 0))
any_success_ax = plt.subplot2grid((3, 2), (0, 1))
reach_exemplar_contact_ax = plt.subplot2grid((3, 2), (1, 0))
reach_exemplar_noContact_ax = plt.subplot2grid((3, 2), (2, 0))
proportion_contact_ax = plt.subplot2grid((3, 2), (1, 1))
proportion_noContact_ax = plt.subplot2grid((3, 2), (2, 1))

# Turn axes off for subplots that will be images added in illustrator
reach_exemplar_contact_ax.axis("off")
reach_exemplar_noContact_ax.axis("off")

# Plot: Total Trials
sns.lineplot(ax=total_trials_ax, x="session_num", y="total_trials",
             hue='genotype', hue_order=["Control", "Knock-Out"], palette=genotype_palette,
             data=trials_per_mouse_per_session, legend=False,
             linewidth=line_width,
             errorbar="se", err_style="bars",
             err_kws={'capsize': cap_size, 'capthick': cap_thick, 'elinewidth': err_line_width})
total_trials_ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])

_, y_err_vals = total_trials_ax.get_lines()[3].get_data()
total_trials_ax.annotate('*\n*',
                         xy=(13, y_err_vals[12]),
                         xytext=(13, y_err_vals[12]),
                         xycoords='data',
                         ha='center',
                         linespacing=any_success_linespacing)
for tDay in [1, 5, 6, 7, 8, 9, 10, 11, 12, 14]:
    total_trials_ax.annotate('*\n*\n*',
                             xy=(tDay, y_err_vals[tDay - 1]),
                             xytext=(tDay, y_err_vals[tDay - 1]),
                             xycoords='data',
                             ha='center',
                             linespacing=any_success_linespacing)

_, y_err_vals = total_trials_ax.get_lines()[7].get_data()
for tDay in [16, 17, 20]:
    total_trials_ax.annotate('*\n*\n*',
                             xy=(tDay, y_err_vals[tDay - 1]),
                             xytext=(tDay, y_err_vals[tDay - 1]),
                             xycoords='data',
                             ha='center',
                             linespacing=any_success_linespacing)
for tDay in [18, 19, 21]:
    total_trials_ax.annotate('*\n*',
                             xy=(tDay, y_err_vals[tDay - 1]),
                             xytext=(tDay, y_err_vals[tDay - 1]),
                             xycoords='data',
                             ha='center',
                             linespacing=any_success_linespacing)
total_trials_ax.annotate('*',
                         xy=(15, y_err_vals[14]),
                         xytext=(15, y_err_vals[14]),
                         xycoords='data',
                         ha='center',
                         linespacing=any_success_linespacing)

total_trials_ax.set(xlabel='training day', ylabel='# trials')
total_trials_ax.spines['top'].set_visible(False)
total_trials_ax.spines['right'].set_visible(False)

# Plot: Any Success
sns.lineplot(ax=any_success_ax, x="session_num", y="any_success",
             hue='genotype', hue_order=["Control", "Knock-Out"], palette=genotype_palette,
             data=reach_scores_by_eartag_by_session_df, legend=True,
             linewidth=line_width,
             errorbar="se", err_style="bars",
             err_kws={'capsize': cap_size, 'capthick': cap_thick, 'elinewidth': err_line_width})
any_success_ax.set_ylim(0, 0.4)
any_success_ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
any_success_ax.set_xticklabels([None] * 11)
any_success_ax.set_yticks([0.10, 0.20, 0.30, 0.40])
any_success_ax.set_yticklabels([10, 20, 30, 40])

_, y_err_vals = any_success_ax.get_lines()[3].get_data()
for tDay in [7, 12, 15]:
    any_success_ax.annotate('*',
                            xy=(tDay, y_err_vals[tDay - 1]),
                            xytext=(tDay, y_err_vals[tDay - 1]),
                            xycoords='data',
                            ha='center')
any_success_ax.annotate('*\n*',
                        xy=(10, y_err_vals[9]),
                        xycoords='data',
                        ha='center',
                        linespacing=any_success_linespacing)
any_success_ax.annotate('*\n*\n*',
                        xy=(6, y_err_vals[5]),
                        xycoords='data',
                        ha='center',
                        linespacing=any_success_linespacing)
labels = ['control', 'Dlx-CKO']
any_success_ax.legend(title=None, labels=labels)
any_success_ax.set(xlabel=None, ylabel='% success')
any_success_ax.spines['top'].set_visible(False)
any_success_ax.spines['right'].set_visible(False)

# Plot: Proportion Contact Trials
sns.lineplot(ax=proportion_contact_ax, x="session_num", y="failure_rate_score_4",
             hue='genotype', hue_order=["Control", "Knock-Out"], palette=genotype_palette,
             data=reach_scores_by_eartag_by_session_df, legend=False,
             linewidth=line_width,
             errorbar="se", err_style="bars",
             err_kws={'capsize': cap_size, 'capthick': cap_thick, 'elinewidth': err_line_width})

proportion_contact_ax.set_ylim(0, 1)
proportion_contact_ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
proportion_contact_ax.set_xticklabels([None] * 11)
proportion_contact_ax.set_yticks([.25, .50, .75, 1.00])
proportion_contact_ax.set_yticklabels([25, 50, 75, 100])
proportion_contact_ax.set(title=None, xlabel=None, ylabel='pellet displaced')

_, y_err_vals = proportion_contact_ax.get_lines()[6].get_data()
for tDay in [1, 3, 4, 9, 10, 12, 13]:
    proportion_contact_ax.annotate('*',
                                   xy=(tDay, y_err_vals[tDay - 1] - 0.13),
                                   xycoords='data',
                                   ha='center')
for tDay in [6, 7]:
    proportion_contact_ax.annotate('*\n*\n*',
                                   xy=(tDay, y_err_vals[tDay - 1] - 0.25),
                                   xycoords='data',
                                   ha='center',
                                   linespacing=any_success_linespacing)

# Plot: Proportion No Contact Trials
sns.lineplot(ax=proportion_noContact_ax, x="session_num", y="failure_rate_score_5",
             hue='genotype', hue_order=["Control", "Knock-Out"], palette=genotype_palette,
             data=reach_scores_by_eartag_by_session_df, legend=False,
             linewidth=line_width,
             errorbar="se", err_style="bars",
             err_kws={'capsize': cap_size, 'capthick': cap_thick, 'elinewidth': err_line_width})

proportion_noContact_ax.set_ylim(0, 1)
proportion_noContact_ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
proportion_noContact_ax.set_yticks([.25, .50, .75, 1.00])
proportion_noContact_ax.set_yticklabels([25, 50, 75, 100])
proportion_noContact_ax.set(title=None, xlabel='training day', ylabel='pellet remains')

_, y_err_vals = proportion_noContact_ax.get_lines()[7].get_data()
for tDay in [1, 2, 9, 12, 13]:
    proportion_noContact_ax.annotate('*',
                                     xy=(tDay, y_err_vals[tDay - 1]),
                                     xytext=(tDay, y_err_vals[tDay - 1]),
                                     xycoords='data',
                                     ha='center')
for tDay in [3, 5, 10]:
    proportion_noContact_ax.annotate('*\n*',
                                     xy=(tDay, y_err_vals[tDay - 1]),
                                     xycoords='data',
                                     ha='center',
                                     linespacing=any_success_linespacing)
for tDay in [6, 7]:
    proportion_noContact_ax.annotate('*\n*\n*',
                                     xy=(tDay, y_err_vals[tDay - 1]),
                                     xycoords='data',
                                     ha='center',
                                     linespacing=any_success_linespacing)
proportion_contact_ax.spines['top'].set_visible(False)
proportion_contact_ax.spines['right'].set_visible(False)

proportion_noContact_ax.spines['top'].set_visible(False)
proportion_noContact_ax.spines['right'].set_visible(False)
# Closing Figure Settings
plt.tight_layout(pad=1)
plt.savefig('/Users/Krista/Desktop/figures/fig1_20220130.pdf')

matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"
plt.rcParams['xtick.major.pad'] = -0.5
plt.rcParams['ytick.major.pad'] = -0.5
cap_size = 4
cap_thick = 1.5
err_line_width = 1.5
line_width = 1.5
dashed_lines = (2, 1)
any_success_linespacing = 0.25
sns.set_theme(context='paper', style="white")
figure = plt.figure(figsize=(4, 3))
figure.set_dpi(1000)

genotype_palette = {"Control": "#005AB5", "Knock-Out": "#DC3220"}
ax = sns.lineplot(x="session_num", y="percent_ab_movt",
                  hue='genotype', hue_order=["Control", "Knock-Out"], palette=genotype_palette,
                  data=abnormal_movt_by_session_df, legend=True,
                  linewidth=line_width,
                  errorbar="se", err_style="bars",
                  err_kws={'capsize': cap_size, 'capthick': cap_thick, 'elinewidth': err_line_width})
ax.set_ylim(0, 0.25)
ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
ax.set_yticks([0.05, 0.1, 0.15, 0.2])
ax.set_yticklabels([5, 10, 15, 20])
labels = ['control', 'Dlx-CKO']
ax.legend(title=None, labels=labels)
ax.set(xlabel='training day', ylabel='% trials')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('/Users/Krista/Desktop/figures/abmov_20220130.pdf')
