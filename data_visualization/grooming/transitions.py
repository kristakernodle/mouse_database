import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

import database_pkg.Models.experiments
from database_pkg import GroomingBout, GroomingSummary
import database_pkg.Models.super_classes

save_dir = '/Users/Krista/OneDrive - Umich/grooming'

palette = {"Control": 'b', "Knock-Out": 'r'}

experiment = database_pkg.Models.experiments.Experiment.get_by_name("grooming")

grooming_data_by_bout = list()

bout: GroomingBout
for bout in experiment.grooming_bouts:

    grooming_summary = GroomingSummary.query.get(bout.grooming_summary_id)
    session = database_pkg.Models.sessions.Session.query.get(bout.session_id)
    mouse = database_pkg.Models.mice.Mouse.query.get(session.mouse_id)

    if mouse.genotype:
        genotype = 'Knock-Out'
    else:
        genotype = 'Control'

    grooming_data_by_bout.append({
        'eartag': mouse.eartag,
        'genotype': genotype,
        'birthdate': mouse.birthdate,
        'sex': mouse.sex,
        'session_date': session.session_date,
        'session_dir': session.session_dir,
        'scored_session_dir': grooming_summary.scored_session_dir,
        'trial_num': grooming_summary.trial_num,
        'total_num_transitions': bout.total_num_transitions,
        'num_incorrect_transitions': bout.num_incorrect_transitions,
        'bout_complete': bout.complete,
        'bout_interrupted': bout.interrupted,
    })

bouts_df = pd.DataFrame.from_records(grooming_data_by_bout)
DATE = 20210211
bouts_df.to_csv(f"{save_dir}/all_bouts_{DATE}.csv")

bouts_df.insert(bouts_df.shape[1], "Percent Incorrect Transitions",
                bouts_df["num_incorrect_transitions"] / bouts_df["total_num_transitions"] * 100)

# Analysis here
#   1. Average number of transitions per bout by genotype
#   2. Percent incorrect transitions
#   3. Total number of transitions by genotype
#   4. Percent interrupted bouts
#   5. Percent incomplete bouts

bouts_count = bouts_df.groupby(['eartag', 'genotype']).count().reset_index()
bouts_sum = bouts_df[['eartag', 'genotype', 'total_num_transitions', 'num_incorrect_transitions', 'bout_complete',
                      'bout_interrupted']] \
    .groupby(['eartag', 'genotype']) \
    .sum().reset_index()

bouts_sum.insert(bouts_sum.shape[1], 'Number of bouts', bouts_count['birthdate'])

bouts_sum.insert(bouts_sum.shape[1], 'Average number of transitions per bout',
                 bouts_sum['total_num_transitions'] / bouts_sum['Number of bouts'])

bouts_sum.insert(bouts_sum.shape[1], 'Percent incorrect transitions',
                 bouts_sum['num_incorrect_transitions'] / bouts_sum['total_num_transitions'] * 100)

bouts_sum.insert(bouts_sum.shape[1], 'Percent incomplete bouts',
                 (bouts_sum['Number of bouts'] - bouts_sum['bout_complete']) / bouts_sum['Number of bouts'] * 100)

bouts_sum.insert(bouts_sum.shape[1], 'Percent interrupted bouts',
                 bouts_sum['bout_interrupted'] / bouts_sum['Number of bouts'] * 100)

#   1. Average number of transitions per bout by genotype
a_file_name = 'average_num_transitions_per_bout.jpeg'
avg_trans_fig = sns.barplot(x='genotype',
                            y='Average number of transitions per bout',
                            data=bouts_sum,
                            palette=palette,
                            capsize=0.2)
avg_trans_fig.set_xlabel('')
avg_trans_fig.set_ylabel('Number of transitions')
plt.savefig(str(Path(save_dir).joinpath(a_file_name)))
plt.close()

#   2. Percent of incorrect transitions
a_file_name = 'percent_incorrect_transitions.jpeg'
incorrect_trans_fig = sns.barplot(x='genotype',
                                  y='Percent incorrect transitions',
                                  data=bouts_sum,
                                  palette=palette,
                                  capsize=0.2)
incorrect_trans_fig.set_xlabel('')
incorrect_trans_fig.set_ylabel('Percent of total transitions')
plt.savefig(str(Path(save_dir).joinpath(a_file_name)))
plt.close()

#   3. Number of transitions
a_file_name = 'num_transitions.jpeg'
num_trans_fig = sns.barplot(x='genotype',
                            y='total_num_transitions',
                            data=bouts_sum,
                            palette=palette,
                            capsize=0.2)
num_trans_fig.set_xlabel('')
num_trans_fig.set_ylabel('Number of transitions')
plt.savefig(str(Path(save_dir).joinpath(a_file_name)))
plt.close()

#   4. Percent interrupted bouts
a_file_name = 'percent_interrupted_bouts.jpeg'
perc_interrupted_fig = sns.barplot(x='genotype',
                                   y='Percent interrupted bouts',
                                   data=bouts_sum,
                                   palette=palette,
                                   capsize=0.2)
perc_interrupted_fig.set_xlabel('')
perc_interrupted_fig.set_ylabel('Percent of bouts')
plt.savefig(str(Path(save_dir).joinpath(a_file_name)))
plt.close()

#   5. Percent incomplete bouts
a_file_name = 'percent_incomplete_bouts.jpeg'
perc_interrupted_fig = sns.barplot(x='genotype',
                                   y='Percent incomplete bouts',
                                   data=bouts_sum,
                                   palette=palette,
                                   capsize=0.2)
perc_interrupted_fig.set_xlabel('')
perc_interrupted_fig.set_ylabel('Percent of bouts')
plt.savefig(str(Path(save_dir).joinpath(a_file_name)))
plt.close()

## Incorrect transition type by genotype
all_incorrect_transitions = list()

bout: GroomingBout
for bout in experiment.grooming_bouts:

    grooming_summary = GroomingSummary.query.get(bout.grooming_summary_id)
    session = database_pkg.Models.sessions.Session.query.get(bout.session_id)
    mouse = database_pkg.Models.mice.Mouse.query.get(session.mouse_id)

    if mouse.genotype:
        genotype = 'Knock-Out'
    else:
        genotype = 'Control'

    new_row = {'eartag': mouse.eartag,
               'genotype': genotype,
               'birthdate': mouse.birthdate,
               'sex': mouse.sex,
               'session_date': session.session_date,
               'session_dir': session.session_dir,
               'scored_session_dir': grooming_summary.scored_session_dir,
               'trial_num': grooming_summary.trial_num,
               'total_num_transitions': bout.total_num_transitions}

    incorrect_transition_details = {
        'Aborted': len(bout.aborted_transitions),
        'Skipped': len(bout.skipped_transitions),
        'Reversed': len(bout.reversed_transitions),
        'Incorrect initiation': len(bout.initiation_incorrect_transitions)
    }
    for key in incorrect_transition_details.keys():
        this_row = dict(**new_row,
                        **{'Transition Type': key,
                           'Number of Transitions': incorrect_transition_details[key]})
        all_incorrect_transitions.append(this_row)

all_incorrect_transitions_df = pd.DataFrame.from_records(all_incorrect_transitions)
DATE = 20210211
all_incorrect_transitions_df.to_csv(f"{save_dir}/all_incorrect_transitions_{DATE}.csv")

all_incorrect_transitions_df.insert(all_incorrect_transitions_df.shape[1],
                                    'Percent of incorrect transitions',
                                    all_incorrect_transitions_df['Number of Transitions'] /
                                    all_incorrect_transitions_df['total_num_transitions'] * 100)

g = sns.catplot(data=all_incorrect_transitions_df,
                kind='bar',
                x="Transition Type",
                y="Percent of incorrect transitions",
                hue='genotype',
                palette=palette,
                legend=False,
                capsize=0.2)
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('incorrect_transition_type_by_genotype.jpeg')), bbox_inches='tight')
plt.close()
