import database_pkg as dbpkg
import pandas as pd
import seaborn
import matplotlib.pyplot as plt

list_all_scored_trials = list()

total_trials = 0
KO_trials_with_AM = 0
CT_trials_with_AM = 0

experiment = dbpkg.Experiment.query.filter(dbpkg.Experiment.experiment_name == 'skilled-reaching').first()

all_scored_trials = dbpkg.SRTrialScore.query.all()

for scored_trial in all_scored_trials:
    trial = dbpkg.Trial.query.get(scored_trial.trial_id)
    reviewer = dbpkg.Reviewer.query.get(scored_trial.reviewer_id)
    folder = dbpkg.Folder.query.get(trial.folder_id)
    session = dbpkg.Session.query.get(trial.session_id)
    mouse = dbpkg.Mouse.query.get(session.mouse_id)

    if session.experiment_id != experiment.experiment_id \
            or trial is None \
            or reviewer is None \
            or folder is None \
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

all_scored_trials_df = pd.DataFrame.from_records(all_scored_trials)
all_scored_trials_one_reviewer_df = all_scored_trials_df.drop_duplicates(subset=['trial_dir'], keep='first')

KO_trial_count_abmov = all_scored_trials_one_reviewer_df[all_scored_trials_one_reviewer_df.genotype == 'Knock-Out'].sum()['abnormal_movt_score']
CT_trial_count_abmov = all_scored_trials_one_reviewer_df[all_scored_trials_one_reviewer_df.genotype == 'Control'].sum()['abnormal_movt_score']

KO_trial_count_grooming = all_scored_trials_one_reviewer_df[all_scored_trials_one_reviewer_df.genotype == 'Knock-Out'].sum()['grooming_score']
CT_trial_count_grooming = all_scored_trials_one_reviewer_df[all_scored_trials_one_reviewer_df.genotype == 'Control'].sum()['grooming_score']

all_trials = len(all_scored_trials_one_reviewer_df)

proportion_KO_abmov = KO_trial_count_abmov/all_trials
proportion_CT_abmov = CT_trial_count_abmov/all_trials

proportion_KO_grooming = KO_trial_count_grooming/all_trials
proportion_CT_grooming = CT_trial_count_grooming/all_trials

count_CT_by_day = all_scored_trials_one_reviewer_df[all_scored_trials_one_reviewer_df.genotype == 'Control'].groupby(all_scored_trials_one_reviewer_df.session_num).count()['session_dir']
count_KO_by_day = all_scored_trials_one_reviewer_df[all_scored_trials_one_reviewer_df.genotype == 'Knock-Out'].groupby(all_scored_trials_one_reviewer_df.session_num).count()['session_dir']

abmov_CT_by_day = all_scored_trials_one_reviewer_df[all_scored_trials_one_reviewer_df.genotype == 'Control'].groupby(all_scored_trials_one_reviewer_df.session_num).count()['abnormal_movt_score']
abmov_KO_by_day = all_scored_trials_one_reviewer_df[all_scored_trials_one_reviewer_df.genotype == 'Knock-Out'].groupby(all_scored_trials_one_reviewer_df.session_num).count()['abnormal_movt_score']

proportion_CT_abmov_by_day = abmov_CT_by_day/count_CT_by_day
proportion_KO_abmov_by_day = abmov_KO_by_day/count_KO_by_day


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

g, ax2 = plt.subplots()
seaborn.set_theme(context='poster', style="whitegrid", font_scale=1.25)
seaborn.set(font_scale=1.25)
seaborn.scatterplot(x="Session Number", y='Percent Trials with Abnormal Movement', hue='Genotype',
                    data=proportions_by_day_df)
ax2.set_title("Trials with Abnormal Movements by Session and Genotype")
# ax2.set(ylim=(0, 10))
# handles, labels = ax2.get_legend_handles_labels()
# ax2.legend(handles[0:2], ('Control', 'Knock-Out'))
plt.subplots_adjust(bottom=0.15)
plt.savefig('/Users/Krista/Desktop/percent_abnormal_movement_by_day_scatterplot.pdf')