import database_pkg as dbpkg
import pandas as pd
import seaborn
import matplotlib.pyplot as plt

list_all_scored_trials = list()

total_trials = 0
KO_trials_with_AM = 0
CT_trials_with_AM = 0


experiment = dbpkg.Experiment.query.filter(dbpkg.Experiment.experiment_name == 'skilled-reaching').first()

for folder in experiment.folders:
    all_blind_folders = folder.score_folders

    if len(all_blind_folders) == 0:
        continue

    elif len(all_blind_folders) > 1:
        # Kenny: 11, Dan: 49, Jen: 114, Alli C: 150, Krista: Too Many, Alli B: 0
        reviewers_by_num_videos_scored = ('Kenny F', 'Dan L', 'Jen M', 'Alli C', 'Krista K', 'Alli B')
        blind_folder_reviewer_list_dict = list()
        for blind_folder in all_blind_folders:
            reviewer = dbpkg.Reviewer.query.get(blind_folder.reviewer_id)
            reviewer_name = f"{reviewer.first_name} {reviewer.last_name}"
            blind_folder_dict = blind_folder.as_dict()
            blind_folder_dict.update({'reviewer_priority': reviewers_by_num_videos_scored.index(reviewer_name)})
            blind_folder_reviewer_list_dict.append(blind_folder_dict)

        blind_folder_reviewer_list_dict.sort(key=lambda i: i['reviewer_priority'])

        blind_folder_dict = blind_folder_reviewer_list_dict[0]
        blind_folder = dbpkg.BlindFolder.query.get(blind_folder_dict['blind_folder_id'])

    else:
        blind_folder = all_blind_folders[0]

    reviewer = dbpkg.Reviewer.query.get(blind_folder.reviewer_id)

    for blind_trial in blind_folder.blind_trials:

        trial = dbpkg.Trial.query.get(blind_trial.trial_id)
        scored_trial = dbpkg.SRTrialScore.query.filter(dbpkg.SRTrialScore.trial_id == trial.trial_id,
                                                       dbpkg.SRTrialScore.reviewer_id == reviewer.reviewer_id).first()
        session = dbpkg.Session.query.get(trial.session_id)
        mouse = dbpkg.Mouse.query.get(session.mouse_id)

        if session.experiment_id != experiment.experiment_id \
                or reviewer is None \
                or trial is None \
                or scored_trial is None \
                or session is None \
                or mouse is None:
            continue

        total_trials += 1
        if mouse.genotype:
            genotype = 'Knock-Out'
            KO_trials_with_AM += 1
        else:
            genotype = 'Control'
            CT_trials_with_AM += 1

        list_all_scored_trials.append(
            {'eartag': mouse.eartag,
             'genotype': genotype,
             'birthdate': mouse.birthdate,
             'sex': mouse.sex,
             'session_num': session.session_num,
             'session_date': session.session_date,
             'session_dir': session.session_dir,
             'folder_dir': folder.folder_dir,
             'reviewer': f"{reviewer.first_name} {reviewer.last_name[0]}",
             'trial_dir': trial.trial_dir,
             'reach_score': scored_trial.reach_score,
             'abnormal_movt_score': scored_trial.abnormal_movt_score,
             'grooming_score': scored_trial.grooming_score
             }
        )

all_scored_trials_df = pd.DataFrame.from_records(list_all_scored_trials)

reach_scores_by_session_dir = all_scored_trials_df.groupby(all_scored_trials_df.session_dir)['reach_score']\
    .value_counts()\
    .unstack()\
    .fillna(0)

reach_scores_by_eartag_by_session_list_dict = list()
for session_dir, all_reach_score_counts in reach_scores_by_session_dir.iterrows():
    session = dbpkg.Session.query.filter(dbpkg.Session.session_dir == session_dir).first()
    mouse = dbpkg.Mouse.query.get(session.mouse_id)

    total_trials += 1
    if mouse.genotype:
        genotype = 'Knock-Out'
        KO_trials_with_AM += 1
    else:
        genotype = 'Control'
        CT_trials_with_AM += 1

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

reach_scores_by_eartag_by_session_df.insert(17, "Total Trials",
                                            reach_scores_by_eartag_by_session_df.iloc[:, 7:].sum(axis=1))
reach_scores_by_eartag_by_session_df.insert(18, "Viable Trials",
                                            reach_scores_by_eartag_by_session_df.iloc[:, 8:13].sum(axis=1))

reach_scores_by_eartag_by_session_df.insert(19, "First Success",
                                            reach_scores_by_eartag_by_session_df['1'] *
                                            100 / reach_scores_by_eartag_by_session_df['Viable Trials'])
reach_scores_by_eartag_by_session_df['First Success'] = reach_scores_by_eartag_by_session_df['First Success'].fillna(0)

reach_scores_by_eartag_by_session_df.insert(20, "Any Success",
                                            (reach_scores_by_eartag_by_session_df['1'] +
                                             reach_scores_by_eartag_by_session_df['2']) * 100 /
                                            reach_scores_by_eartag_by_session_df['Viable Trials'])
reach_scores_by_eartag_by_session_df['Any Success'] = reach_scores_by_eartag_by_session_df['Any Success'].fillna(0)


KO_trials_with_abmov = all_scored_trials_df[(all_scored_trials_df['genotype'] == 'Knock-Out') &
                                            (all_scored_trials_df['abnormal_movt_score'] is True)]

KO_trial_count_abmov = all_scored_trials_df[all_scored_trials_df.genotype == 'Knock-Out'].sum()['abnormal_movt_score']
CT_trial_count_abmov = all_scored_trials_df[all_scored_trials_df.genotype == 'Control'].sum()['abnormal_movt_score']

KO_trial_count_grooming = all_scored_trials_df[all_scored_trials_df.genotype == 'Knock-Out'].sum()['grooming_score']
CT_trial_count_grooming = all_scored_trials_df[all_scored_trials_df.genotype == 'Control'].sum()['grooming_score']

all_trials = len(all_scored_trials_df)

proportion_KO_abmov = KO_trial_count_abmov/all_trials
proportion_CT_abmov = CT_trial_count_abmov/all_trials

proportion_KO_grooming = KO_trial_count_grooming/all_trials
proportion_CT_grooming = CT_trial_count_grooming/all_trials

count_CT_by_day = all_scored_trials_df[all_scored_trials_df.genotype == 'Control'].groupby(all_scored_trials_df.session_num).count()['session_dir']
count_KO_by_day = all_scored_trials_df[all_scored_trials_df.genotype == 'Knock-Out'].groupby(all_scored_trials_df.session_num).count()['session_dir']

abmov_CT_by_day = all_scored_trials_df[all_scored_trials_df.genotype == 'Control'].groupby(all_scored_trials_df.session_num).count()['abnormal_movt_score']
abmov_KO_by_day = all_scored_trials_df[all_scored_trials_df.genotype == 'Knock-Out'].groupby(all_scored_trials_df.session_num).count()['abnormal_movt_score']

proportion_CT_abmov_by_day = abmov_CT_by_day/count_CT_by_day
proportion_KO_abmov_by_day = abmov_KO_by_day/count_KO_by_day

num_first_success_by_session_dir = all_scored_trials_df[all_scored_trials_df.reach_score == 1]\
    .grouby(all_scored_trials_df.session_dir)\
    .count()['trial_dir']

num_second_success_by_session_dir = all_scored_trials_df[all_scored_trials_df.reach_score == 2]\
    .grouby(all_scored_trials_df.session_dir)\
    .count()['trial_dir']

num_viable_trials_by_session_dir = all_scored_trials_df[all_scored_trials_df.reach_score != 0]\
    .grouby(all_scored_trials_df.session_dir)\
    .count()['trial_dir']

list_proportions_by_day = list()
for session_num in range(1, 22):
    series_index = session_num-1
    list_proportions_by_day.append({
        'Session Number': session_num,
        'Genotype': 'Control',
        'Proportion Trials with Abnormal Movements': proportion_CT_abmov_by_day.iloc[series_index]
    })
    list_proportions_by_day.append({
        'Session Number': session_num,
        'Genotype': 'Knock-Out',
        'Proportion Trials with Abnormal Movements': proportion_KO_abmov_by_day.iloc[series_index]
    })

proportions_by_day_df = pd.DataFrame.from_records(list_proportions_by_day)
proportions_by_day_df['Percent Trials with Abnormal Movement'] = proportions_by_day_df['Proportion Trials with Abnormal Movements']*100

palette = {"Control": 'b', "Knock-Out": 'r'}
g, ax2 = plt.subplots()
seaborn.set_theme(context='poster', style="whitegrid", font_scale=1.25)
seaborn.set(font_scale=1.25)
seaborn.scatterplot(x="Session Number", y='Percent Trials with Abnormal Movement', hue='Genotype', palette=palette,
                    data=proportions_by_day_df)
ax2.set_title("Trials with Abnormal Movements by Session and Genotype")
# ax2.set(ylim=(0, 10))
# handles, labels = ax2.get_legend_handles_labels()
# ax2.legend(handles[0:2], ('Control', 'Knock-Out'))
plt.subplots_adjust(bottom=0.15)
plt.savefig('/Users/Krista/Desktop/percent_abnormal_movement_by_day_scatterplot.pdf')


h, ax3 = plt.subplots()
seaborn.set_theme(context='poster', style="whitegrid", font_scale=1.25)
seaborn.set(font_scale=1.25)
seaborn.boxplot(x="session_num", y="First Success", hue='genotype', palette=palette,
                data=reach_scores_by_eartag_by_session_df)
ax3.set_title("Single Pellet Skilled-Reaching First Success Rate by Genotype")
ax3.set(xlabel="Training Day", ylabel='Percent Success')
plt.legend(title='Genotype')
handles, labels = ax3.get_legend_handles_labels()
handles_labels = list(zip(handles, labels))
handles_labels = sorted(handles_labels, key=lambda group: group[1])
unzipped_handles_labels = list(zip(*handles_labels))
ax3.legend(unzipped_handles_labels[0], unzipped_handles_labels[1])
plt.subplots_adjust(bottom=0.15)
plt.savefig('/Users/Krista/Desktop/figures/first_success_rate_boxplot.pdf')

j, ax4 = plt.subplots()
seaborn.set_theme(context='poster', style="whitegrid", font_scale=1.25)
seaborn.set(font_scale=1.25)
seaborn.boxplot(x="session_num", y="Any Success", hue='genotype', palette=palette,
                data=reach_scores_by_eartag_by_session_df)
ax4.set_title("Single Pellet Skilled-Reaching Any Success Rate by Genotype")
ax4.set(xlabel="Training Day", ylabel='Percent Success')
plt.legend(title='Genotype')
handles, labels = ax4.get_legend_handles_labels()
handles_labels = list(zip(handles, labels))
handles_labels = sorted(handles_labels, key=lambda group: group[1])
unzipped_handles_labels = list(zip(*handles_labels))
ax4.legend(unzipped_handles_labels[0], unzipped_handles_labels[1])
plt.subplots_adjust(bottom=0.15)
plt.savefig('/Users/Krista/Desktop/figures/any_success_rate_boxplot.pdf')
