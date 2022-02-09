import pandas as pd

from database_pkg import Mouse, Experiment, Session, SRTrialScore, Trial, Reviewer
import matplotlib.pyplot as plt
import seaborn as sns

experiment = Experiment.get_by_name('dlxCKO-chatSap-skilled-reaching')

all_scored_trials_list = SRTrialScore.query.join(Trial, SRTrialScore.trial_id == Trial.trial_id).filter(
    Trial.experiment_id == experiment.experiment_id).all()

all_scored_trials_listdict = list()
for scored_trial in all_scored_trials_list:
    trial = Trial.query.get(scored_trial.trial_id)
    session = Session.query.get(trial.session_id)
    mouse = Mouse.query.get(session.mouse_id)
    reviewer = Reviewer.query.get(scored_trial.reviewer_id)

    all_scored_trials_listdict.append(
        {'eartag': mouse.eartag,
         'genotype': mouse.genotype,
         'birthdate': mouse.birthdate,
         'sex': mouse.sex,
         'session_dir': session.session_dir,
         'session_num': session.session_num,
         'session_date': session.session_date,
         'experiment_phase': session.experiment_phase,
         'reviewer': f"{reviewer.first_name} {reviewer.last_name}",
         'trial_dir': trial.trial_dir,
         'reach_score': scored_trial.reach_score,
         'abnormal_movt_score': scored_trial.abnormal_movt_score,
         'grooming_score': scored_trial.grooming_score})

all_scored_trials = pd.DataFrame.from_records(all_scored_trials_listdict)

viable_scored_trials = all_scored_trials[all_scored_trials.reach_score != 7]

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
         'experiment_phase': session.experiment_phase,
         'abnormal_movt_count': abnormal_movt_count[True],
         'percent_ab_movt': abnormal_movt_count[True] / (abnormal_movt_count[True] + abnormal_movt_count[False])})

abnormal_movt_by_session_df = pd.DataFrame.from_records(abnormal_movt_by_eartag_by_session_list_dict)

for index, row in abnormal_movt_by_session_df.loc[
    abnormal_movt_by_session_df['experiment_phase'] == 'PreSurgery'].iterrows():
    abnormal_movt_by_session_df.at[index, 'session_num'] = 0

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
         'experiment_phase': session.experiment_phase,
         '1': all_reach_score_counts[1],
         '2': all_reach_score_counts[2],
         '3': all_reach_score_counts[3],
         '4': all_reach_score_counts[4],
         '5': all_reach_score_counts[5],
         '7': all_reach_score_counts[7]
         })

reach_scores_by_eartag_by_session_df = pd.DataFrame.from_records(reach_scores_by_eartag_by_session_list_dict)

reach_scores_by_eartag_by_session_df.insert(reach_scores_by_eartag_by_session_df.shape[1], "total_trials",
                                            reach_scores_by_eartag_by_session_df.iloc[:, 8:].count(axis=1))
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

for index, row in reach_scores_by_eartag_by_session_df.loc[
    reach_scores_by_eartag_by_session_df['experiment_phase'] == 'PreSurgery'].iterrows():
    reach_scores_by_eartag_by_session_df.at[index, 'session_num'] = 0

####

fig = plt.figure()
fig.subplots_adjust(bottom=0.025, left=0.025, top=0.975, right=0.975)

ax = plt.subplot2grid((1, 2), (0, 0), colspan=2)

ab_movt = sns.lineplot(ax=ax, x="session_num", y="percent_ab_movt",
                       data=abnormal_movt_by_session_df, hue='experiment_phase',
                       palette={'PreSurgery': 'b', 'PostSurgery': 'r'}, legend=True,
                       errorbar="se", err_style="bars", err_kws={'capsize': 4, 'capthick': 2, 'elinewidth': 2})

mean_pts = sns.pointplot(ax=ax, x="session_num", y="percent_ab_movt", hue='experiment_phase',
                         data=abnormal_movt_by_session_df, palette={'PreSurgery': 'b', 'PostSurgery': 'r'}, markers='o',
                         errwidth=0, legend=False)

pre_ab_movt_pts = sns.scatterplot(ax=ax, x="session_num", y="percent_ab_movt",
                                  data=abnormal_movt_by_session_df,
                                  hue='eartag', palette={503: 'dimgrey', 576: 'darkgrey', 710: 'lightgrey'}, s=100,
                                  legend=True)

ax.set_xticks([0, 1, 2, 3, 4, 5])
ax.set_xticklabels(['baseline', 1, 2, 3, 4, 5])
ax.set_ylim([0, 0.2])
ax.set_yticks([0, 0.05, 0.1, 0.2])
ax.set_yticklabels([0, 5, 10, 20])
handles, labels = ax.get_legend_handles_labels()
handles = [handles[0], handles[1], handles[4], handles[5], handles[6]]
labels = ['pre surgery', 'post surgery', labels[4], labels[5], labels[6]]
ax.legend(handles=handles, labels=labels)
ax.set_ylabel('percent trials with abnormal movement')
ax.set_xlabel('session number')
ax.set_title('Abnormal Movement Presence')
plt.tight_layout()
plt.savefig('/Users/Krista/OneDrive - Umich/thesis_AC/abnormal_movt_presence.pdf')

####


figure = plt.figure()
figure.subplots_adjust(bottom=0.025, left=0.025, top=0.975, right=0.975)

ax3 = plt.subplot2grid((3, 2), (0, 0), colspan=2)
ax1 = plt.subplot2grid((3, 2), (1, 0), colspan=2)
ax2 = plt.subplot2grid((3, 2), (2, 0), colspan=2)

any_success = sns.lineplot(ax=ax1, x="session_num", y="any_success", hue="experiment_phase",
                           data=reach_scores_by_eartag_by_session_df, legend=False,
                           palette={'PreSurgery': 'b', 'PostSurgery': 'r'},
                           errorbar="se", err_style="bars", err_kws={'capsize': 4, 'capthick': 2, 'elinewidth': 2})
ax1.set_xticks([0, 1, 2, 3, 4, 5])
ax1.set_xticklabels(['baseline', 1, 2, 3, 4, 5])
# atypicalBehavior_ax.legend(handles=[atypicalBehavior_ax.get_lines()[0], atypicalBehavior_ax.get_lines()[4]], labels=['pre surgery', 'post surgery'])
ax1.set_ylabel('percent success')
ax1.set_xlabel(None)
ax1.set_title('any success rate')

first_success = sns.lineplot(ax=ax2, x="session_num", y="first_success", hue="experiment_phase",
                             data=reach_scores_by_eartag_by_session_df, legend=False,
                             palette={'PreSurgery': 'b', 'PostSurgery': 'r'},
                             errorbar="se", err_style="bars", err_kws={'capsize': 4, 'capthick': 2, 'elinewidth': 2})

ax2.set_xticks([0, 1, 2, 3, 4, 5])
ax2.set_xticklabels(['baseline', 1, 2, 3, 4, 5])
# ax2.legend(handles=[ax2.get_lines()[0], ax2.get_lines()[4]], labels=['pre surgery', 'post surgery'])
ax2.set_ylabel('percent success')
ax2.set_xlabel('session number')
ax2.set_title('first success rate')

pre_viable_trials = sns.lineplot(ax=ax3, x="session_num", y="viable_trials", hue="experiment_phase",
                                 data=reach_scores_by_eartag_by_session_df, legend=True,
                                 palette={'PreSurgery': 'b', 'PostSurgery': 'r'},
                                 errorbar="se", err_style="bars",
                                 err_kws={'capsize': 4, 'capthick': 2, 'elinewidth': 2})

ax3.set_xticks([0, 1, 2, 3, 4, 5])
ax3.set_xticklabels(['baseline', 1, 2, 3, 4, 5])
ax3.legend(handles=[ax3.get_lines()[0], ax3.get_lines()[4]], labels=['pre surgery', 'post surgery'])
ax3.set_ylabel('count per session')
ax3.set_title('performed trials')
ax3.set_xlabel(None)

plt.tight_layout()
plt.savefig('/Users/Krista/OneDrive - Umich/thesis_AC/success_rates.pdf')

figure2 = plt.figure()
figure2.set_figwidth(8)
figure2.set_figheight(10)
figure2.subplots_adjust(bottom=0.025, left=0.025, top=0.975, right=0.975)

ax1 = plt.subplot2grid((5, 1), (0, 0), colspan=2)
ax2 = plt.subplot2grid((5, 1), (1, 0), colspan=2)
ax3 = plt.subplot2grid((5, 1), (2, 0), colspan=2)
ax4 = plt.subplot2grid((5, 1), (3, 0), colspan=2)
ax5 = plt.subplot2grid((5, 1), (4, 0), colspan=2)

prop1 = sns.lineplot(ax=ax1, x="session_num", y="prop_1_s", hue="experiment_phase",
                     data=reach_scores_by_eartag_by_session_df, legend=True,
                     palette={'PreSurgery': 'b', 'PostSurgery': 'r'},
                     errorbar="se", err_style="bars", err_kws={'capsize': 4, 'capthick': 2, 'elinewidth': 2})

ax1.set_xticks([0, 1, 2, 3, 4, 5])
ax1.set_ylim([0, 1])
ax1.set_xticklabels(['baseline', 1, 2, 3, 4, 5])
ax1.legend(handles=[ax1.get_lines()[0], ax1.get_lines()[4]], labels=['pre surgery', 'post surgery'])
ax1.set_title('proportion of successful trials with score 1')
ax1.set_xlabel(None)
ax1.set_ylabel(None)

prop2_s = sns.lineplot(ax=ax2, x="session_num", y="prop_2_s",
                       hue="experiment_phase",
                       data=reach_scores_by_eartag_by_session_df, legend=False,
                       palette={'PreSurgery': 'b', 'PostSurgery': 'r'},
                       errorbar="se", err_style="bars", err_kws={'capsize': 4, 'capthick': 2, 'elinewidth': 2})

ax2.set_xticks([0, 1, 2, 3, 4, 5])
ax2.set_ylim([0, 1])
ax2.set_xticklabels(['baseline', 1, 2, 3, 4, 5])
ax2.set_ylabel(None)
ax2.set_title('proportion of successful trials with score 2')
ax2.set_xlabel(None)

prop3_s = sns.lineplot(ax=ax3, x="session_num", y="prop_3_s", hue="experiment_phase",
                       data=reach_scores_by_eartag_by_session_df, legend=False,
                       palette={'PreSurgery': 'b', 'PostSurgery': 'r'},
                       errorbar="se", err_style="bars", err_kws={'capsize': 4, 'capthick': 2, 'elinewidth': 2})

ax3.set_xticks([0, 1, 2, 3, 4, 5])
ax3.set_xticklabels(['baseline', 1, 2, 3, 4, 5])
ax3.set_ylim([0, 1])
ax3.set_ylabel('proportion of trials')
ax3.set_title('proportion of unsuccessful trials with score 3')
ax3.set_xlabel(None)

prop4_s = sns.lineplot(ax=ax4, x="session_num", y="prop_4_s", hue="experiment_phase",
                       data=reach_scores_by_eartag_by_session_df, legend=False,
                       palette={'PreSurgery': 'b', 'PostSurgery': 'r'},
                       errorbar="se", err_style="bars", err_kws={'capsize': 4, 'capthick': 2, 'elinewidth': 2})

ax4.set_xticks([0, 1, 2, 3, 4, 5])
ax4.set_xticklabels(['baseline', 1, 2, 3, 4, 5])
ax4.set_ylim([0, 1])
ax4.set_title('proportion of unsuccessful trials with score 4')
ax4.set_xlabel(None)
ax4.set_ylabel(None)

prop5_s = sns.lineplot(ax=ax5, x="session_num", y="prop_5_s", hue="experiment_phase",
                       data=reach_scores_by_eartag_by_session_df, legend=False,
                       palette={'PreSurgery': 'b', 'PostSurgery': 'r'},
                       errorbar="se", err_style="bars", err_kws={'capsize': 4, 'capthick': 2, 'elinewidth': 2})

ax5.set_xticks([0, 1, 2, 3, 4, 5])
ax5.set_xticklabels(['baseline', 1, 2, 3, 4, 5])
ax5.set_ylim([0, 1])
ax5.set_title('proportion of unsuccessful trials with score 5')
ax5.set_ylabel(None)
ax5.set_xlabel('session number')

plt.tight_layout()
plt.savefig('/Users/Krista/OneDrive - Umich/thesis_AC/score_proportion.pdf')
