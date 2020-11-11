import database_pkg as dbpkg
from random import choice
import pandas as pd
import seaborn
import matplotlib.pyplot as plt

sr_experiment = dbpkg.Experiment.query.filter(dbpkg.Experiment.experiment_name == 'skilled-reaching').first()
all_participants = dbpkg.ParticipantDetail.query.filter(dbpkg.ParticipantDetail.experiment_id == sr_experiment.experiment_id).all()

all_rows = []

for participant in all_participants:
    mouse = dbpkg.Mouse.query.get(participant.mouse_id)
    participant_sessions = dbpkg.Session.query.filter(dbpkg.Session.mouse_id == participant.mouse_id,
                                                      dbpkg.Session.experiment_id == sr_experiment.experiment_id)\
                                .order_by(dbpkg.Session.session_date)
    for session in participant_sessions:
        total_trials = len(session.trials)
        if len(session.trials) == 0:
            print(session.session_dir)
            continue
        viable_trials = total_trials
        count_ab_mov = 0
        count_grooming = 0

        for trial in session.trials:

            if len(trial.scores) > 1:
                trial_score = choice(trial.scores)
            elif len(trial.scores) < 1:
                continue
            else:
                trial_score = trial.scores[0]

            if trial_score.reach_score == 0:
                viable_trials -= 1

            if trial_score.abnormal_movt_score is True:
                count_ab_mov += 1

            if trial_score.grooming_score is True:
                count_grooming += 1

        row_dict = {'Mouse': mouse.eartag, 'Genotype': mouse.genotype, 'Training Day': session.session_num,
                    'Total Trials': total_trials, 'Viable Trials': viable_trials,
                    'Count Trials with Abnormal Movement': count_ab_mov,
                    'Count Trials with Grooming': count_grooming,
                    'Percent Trials with Abnormal Movement': count_ab_mov*100/total_trials,
                    'Percent Trials with Grooming': count_grooming*100/total_trials}

        all_rows.append(row_dict)

booleanMeasures_dataframe = pd.DataFrame(all_rows)
a = booleanMeasures_dataframe.assign(namedGenotype=booleanMeasures_dataframe.Genotype.map({0: "Control", 1: "Knock-Out"}))


f, ax = plt.subplots()
seaborn.set_theme(context='poster', style="whitegrid", font_scale=1.25)
seaborn.set(font_scale=1.25)
seaborn.boxplot(x="Training Day", y='Percent Trials with Abnormal Movement', hue='Genotype', data=booleanMeasures_dataframe, showfliers=False)
seaborn.stripplot(x="Training Day", y='Percent Trials with Abnormal Movement', hue='Genotype', data=booleanMeasures_dataframe)
ax.set_title("Abnormal Movement Presence During Training")
ax.set(ylim=(0, 10))
handles, lables = ax.get_legend_handles_labels()
ax.legend(handles[0:2], ('Control', 'Knock-Out'))
plt.subplots_adjust(bottom=0.15)
plt.savefig('/Users/Krista/Desktop/percent_abnormal_movement_present_boxplot_ylim0-10.pdf')

g, ax2 = plt.subplots()
seaborn.set_theme(context='poster', style="whitegrid", font_scale=1.25)
seaborn.set(font_scale=1.25)
seaborn.scatterplot(x="Training Day", y='Percent Trials with Abnormal Movement', hue='Genotype', data=booleanMeasures_dataframe)
ax2.set_title("Abnormal Movement Presence During Training")
ax2.set(ylim=(0, 10))
handles, labels = ax2.get_legend_handles_labels()
ax2.legend(handles[0:2], ('Control', 'Knock-Out'))
plt.subplots_adjust(bottom=0.15)
plt.savefig('/Users/Krista/Desktop/percent_abnormal_movement_present_scatterplot_ylim0-10.pdf')


