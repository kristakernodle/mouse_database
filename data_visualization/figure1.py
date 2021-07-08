import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

from database_pkg import Mouse, Experiment, Session, SRTrialScore, Trial, Reviewer


def convert_reach_scores_df_proportion_df(genotype_reach_scores):
    proportion_list = list()
    for index, row in genotype_reach_scores.iterrows():
        row_dict = {'eartag': row.eartag,
                    'genotype': row.genotype,
                    'birthdate': row.birthdate,
                    'sex': row.sex,
                    'session_num': row.session_num}

        proportions = {'contact miss': row.prop_4,
                       'no contact miss': row.prop_5}

        for key in proportions.keys():
            this_row = dict(**row_dict,
                            **{'miss_type': key,
                               'value': proportions[key]}
                            )
            proportion_list.append(this_row)
    return pd.DataFrame.from_records(proportion_list)


experiment = Experiment.get_by_name('dlxCKO-skilled-reaching')

all_scored_trials = experiment.get_all_scored_trials()

viable_scored_trials = all_scored_trials.query('reach_score not in [0, 6, 7]')

abnormal_movt_by_session_dir = viable_scored_trials.groupby(viable_scored_trials.session_dir)['abnormal_movt_score'] \
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

reach_scores_by_session_dir = all_scored_trials.groupby(all_scored_trials.session_dir)['reach_score'] \
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

    reach_scores_by_eartag_by_session_list_dict.append(
        {'eartag': mouse.eartag,
         'genotype': genotype,
         'birthdate': mouse.birthdate,
         'sex': mouse.sex,
         'session_num': session.session_num,
         'session_date': session.session_date,
         'session_dir': session.session_dir,
         '0': all_reach_score_counts[0],
         '1': all_reach_score_counts[1],
         '2': all_reach_score_counts[2],
         '3': all_reach_score_counts[3],
         '4': all_reach_score_counts[4],
         '5': all_reach_score_counts[5],
         '6': all_reach_score_counts[6],
         '7': all_reach_score_counts[7],
         '8': all_reach_score_counts[8],
         '9': all_reach_score_counts[9]
         })

reach_scores_by_eartag_by_session_df = pd.DataFrame.from_records(reach_scores_by_eartag_by_session_list_dict)

reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "total_trials",
                                            reach_scores_by_eartag_by_session_df.iloc[:, 7:].count(axis=1))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "viable_trials",
                                            reach_scores_by_eartag_by_session_df.iloc[:,
                                            [8, 9, 10, 11, 12]].sum(axis=1))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "successful_trials",
                                            reach_scores_by_eartag_by_session_df.iloc[:, [8, 9]].sum(axis=1))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "unsuccessful_trials",
                                            reach_scores_by_eartag_by_session_df.iloc[:, [10, 11, 12]].sum(axis=1))

reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "first_success",
                                            reach_scores_by_eartag_by_session_df['1'] *
                                            100 / reach_scores_by_eartag_by_session_df['viable_trials'])
reach_scores_by_eartag_by_session_df['first_success'] = reach_scores_by_eartag_by_session_df[
    'first_success'].fillna(0)

reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "any_success",
                                            (reach_scores_by_eartag_by_session_df['1'] +
                                             reach_scores_by_eartag_by_session_df['2']) * 100 /
                                            reach_scores_by_eartag_by_session_df['viable_trials'])
reach_scores_by_eartag_by_session_df['any_success'] = reach_scores_by_eartag_by_session_df['any_success'].fillna(0)

reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_1', (
        reach_scores_by_eartag_by_session_df['1'] / reach_scores_by_eartag_by_session_df['viable_trials']))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_1_s', (
        reach_scores_by_eartag_by_session_df['1'] / reach_scores_by_eartag_by_session_df['successful_trials']))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_2', (
        reach_scores_by_eartag_by_session_df['2'] / reach_scores_by_eartag_by_session_df['viable_trials']))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_2_s', (
        reach_scores_by_eartag_by_session_df['2'] / reach_scores_by_eartag_by_session_df['successful_trials']))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_3', (
        reach_scores_by_eartag_by_session_df['3'] / reach_scores_by_eartag_by_session_df['viable_trials']))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_3_s', (
        reach_scores_by_eartag_by_session_df['3'] / reach_scores_by_eartag_by_session_df['unsuccessful_trials']))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_4', (
        reach_scores_by_eartag_by_session_df['4'] / reach_scores_by_eartag_by_session_df['viable_trials']))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_4_s', (
        reach_scores_by_eartag_by_session_df['4'] / reach_scores_by_eartag_by_session_df['unsuccessful_trials']))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_5', (
        reach_scores_by_eartag_by_session_df['5'] / reach_scores_by_eartag_by_session_df['viable_trials']))
reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], 'prop_5_s', (
        reach_scores_by_eartag_by_session_df['5'] / reach_scores_by_eartag_by_session_df['unsuccessful_trials']))

reach_scores_by_eartag_by_session_df['prop_1'] = reach_scores_by_eartag_by_session_df['prop_1'].fillna(0)
reach_scores_by_eartag_by_session_df['prop_1_s'] = reach_scores_by_eartag_by_session_df['prop_1_s'].fillna(0)
reach_scores_by_eartag_by_session_df['prop_2'] = reach_scores_by_eartag_by_session_df['prop_2'].fillna(0)
reach_scores_by_eartag_by_session_df['prop_2_s'] = reach_scores_by_eartag_by_session_df['prop_2_s'].fillna(0)
reach_scores_by_eartag_by_session_df['prop_3'] = reach_scores_by_eartag_by_session_df['prop_3'].fillna(0)
reach_scores_by_eartag_by_session_df['prop_3_s'] = reach_scores_by_eartag_by_session_df['prop_3_s'].fillna(0)
reach_scores_by_eartag_by_session_df['prop_4'] = reach_scores_by_eartag_by_session_df['prop_4'].fillna(0)
reach_scores_by_eartag_by_session_df['prop_4_s'] = reach_scores_by_eartag_by_session_df['prop_4_s'].fillna(0)
reach_scores_by_eartag_by_session_df['prop_5'] = reach_scores_by_eartag_by_session_df['prop_5'].fillna(0)
reach_scores_by_eartag_by_session_df['prop_5_s'] = reach_scores_by_eartag_by_session_df['prop_5_s'].fillna(0)

reach_scores_by_eartag_by_session_df.to_csv(
    "/Users/Krista/OneDrive - Umich/figures/reach_scores_by_eartag_by_session_df_20210604.csv")

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
behavior_timeline_ax = plt.subplot2grid((3, 2), (0, 0))
any_success_ax = plt.subplot2grid((3, 2), (0, 1))
reach_exemplar_contact_ax = plt.subplot2grid((3, 2), (1, 0))
reach_exemplar_noContact_ax = plt.subplot2grid((3, 2), (2, 0))
proportion_contact_ax = plt.subplot2grid((3, 2), (1, 1))
proportion_noContact_ax = plt.subplot2grid((3, 2), (2, 1))

# Turn axes off for subplots that will be images added in illustrator
behavior_timeline_ax.axis("off")
reach_exemplar_contact_ax.axis("off")
reach_exemplar_noContact_ax.axis("off")

# Plot: Any Success
sns.lineplot(ax=any_success_ax, x="session_num", y="any_success",
             hue='genotype', hue_order=["Control", "Knock-Out"], palette=genotype_palette,
             data=reach_scores_by_eartag_by_session_df, legend=True,
             linewidth=line_width,
             errorbar="se", err_style="bars",
             err_kws={'capsize': cap_size, 'capthick': cap_thick, 'elinewidth': err_line_width})
any_success_ax.set_ylim(0, 40)
any_success_ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
any_success_ax.set_xticklabels([None]*11)
any_success_ax.set_yticks([10, 20, 30, 40])
# Add significance
# any_success_ax.plot([1, 21], [42, 42], color='black', linewidth=line_width / 2)
# any_success_ax.annotate('*',
#                         xy=(10.5, 42),
#                         xytext=(10.5, 42),
#                         xycoords='data',
#                         ha='center')
_, y_err_vals = any_success_ax.get_lines()[3].get_data()
for tDay in [3, 5, 9, 12, 13, 14, 15, 19]:
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
sns.lineplot(ax=proportion_contact_ax, x="session_num", y="prop_4_s",
             hue='genotype', hue_order=["Control", "Knock-Out"], palette=genotype_palette,
             data=reach_scores_by_eartag_by_session_df, legend=False,
             linewidth=line_width,
             errorbar="se", err_style="bars",
             err_kws={'capsize': cap_size, 'capthick': cap_thick, 'elinewidth': err_line_width})

proportion_contact_ax.set_ylim(0, 1)
proportion_contact_ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
proportion_contact_ax.set_xticklabels([None]*11)
proportion_contact_ax.set_yticks([.25, .50, .75, 1.00])
proportion_contact_ax.set_yticklabels([25, 50, 75, 100])
proportion_contact_ax.set(title=None, xlabel=None, ylabel='pellet contact')
# proportion_contact_ax.plot([1, 21], [0.20, 0.20], color='black', linewidth=line_width / 2)
# proportion_contact_ax.annotate('**',
#                                xy=(10.5, 0.07),
#                                xytext=(10.5, 0.07),
#                                xycoords='data',
#                                ha='center')
_, y_err_vals = proportion_contact_ax.get_lines()[6].get_data()
for tDay in [9, 10, 13, 17]:
    proportion_contact_ax.annotate('*',
                                   xy=(tDay, y_err_vals[tDay - 1] - 0.13),
                                   xycoords='data',
                                   ha='center')
for tDay in [3, 6, 7]:
    proportion_contact_ax.annotate('*\n*',
                                   xy=(tDay, y_err_vals[tDay - 1] - 0.19),
                                   xycoords='data',
                                   ha='center',
                                   linespacing=any_success_linespacing)
proportion_contact_ax.spines['top'].set_visible(False)
proportion_contact_ax.spines['right'].set_visible(False)
# Plot: Proportion No Contact Trials
sns.lineplot(ax=proportion_noContact_ax, x="session_num", y="prop_5_s",
             hue='genotype', hue_order=["Control", "Knock-Out"], palette=genotype_palette,
             data=reach_scores_by_eartag_by_session_df, legend=False,
             linewidth=line_width,
             errorbar="se", err_style="bars",
             err_kws={'capsize': cap_size, 'capthick': cap_thick, 'elinewidth': err_line_width})

proportion_noContact_ax.set_ylim(0, 1)
proportion_noContact_ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
proportion_noContact_ax.set_yticks([.25, .50, .75, 1.00])
proportion_noContact_ax.set_yticklabels([25, 50, 75, 100])
proportion_noContact_ax.set(title=None, xlabel='training day', ylabel='no pellet contact')

# proportion_noContact_ax.plot([1, 21], [0.85, 0.85], color='black', linewidth=line_width / 2)
# proportion_noContact_ax.annotate('***',
#                                  xy=(10.5, 0.85),
#                                  xytext=(10.5, 0.85),
#                                  xycoords='data',
#                                  ha='center')
_, y_err_vals = proportion_noContact_ax.get_lines()[7].get_data()
for tDay in [8, 13]:
    proportion_noContact_ax.annotate('*',
                                     xy=(tDay, y_err_vals[tDay - 1]),
                                     xytext=(tDay, y_err_vals[tDay - 1]),
                                     xycoords='data',
                                     ha='center')
for tDay in [3, 5, 9, 12]:
    proportion_noContact_ax.annotate('*\n*',
                                     xy=(tDay, y_err_vals[tDay - 1]),
                                     xycoords='data',
                                     ha='center',
                                     linespacing=any_success_linespacing)
for tDay in [6, 7, 10]:
    proportion_noContact_ax.annotate('*\n*\n*',
                                     xy=(tDay, y_err_vals[tDay - 1]),
                                     xycoords='data',
                                     ha='center',
                                     linespacing=any_success_linespacing)
proportion_noContact_ax.spines['top'].set_visible(False)
proportion_noContact_ax.spines['right'].set_visible(False)
# Closing Figure Settings
plt.tight_layout(pad=1)
plt.savefig('/Users/Krista/OneDrive - Umich/figures/figures_ai/figure1/fig1_20210708.pdf')
