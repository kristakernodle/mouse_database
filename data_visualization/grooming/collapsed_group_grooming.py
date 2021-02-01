import database_pkg as dbpkg
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

save_dir = '/Users/Krista/OneDrive - Umich/grooming'

palette = {"Control": 'b', "Knock-Out": 'r'}

experiment = dbpkg.Experiment.query.filter_by(experiment_name="grooming").first()

grooming_summary_data = list()
for grooming_summary in experiment.scored_grooming:
    session = dbpkg.Session.query.get(grooming_summary.session_id)
    mouse = dbpkg.Mouse.query.get(session.mouse_id)

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
               }
    trial_details = {'trial_length': grooming_summary.trial_length,
                     'latency_to_onset': grooming_summary.latency_to_onset,
                     'num_bouts': grooming_summary.num_bouts,
                     'total_time_grooming': grooming_summary.total_time_grooming,
                     'num_interrupted_bouts': grooming_summary.num_interrupted_bouts,
                     'num_chains': grooming_summary.num_chains,
                     'num_complete_chains': grooming_summary.num_complete_chains,
                     'avg_time_per_bout': grooming_summary.avg_time_per_bout
                     }
    for key in trial_details.keys():
        this_row = dict(**new_row,
                        **{'trial measure': key,
                           'value': trial_details[key]})
        grooming_summary_data.append(this_row)

grooming_summary_df = pd.DataFrame.from_records(grooming_summary_data)
grooming_summary_df.to_csv('/Users/Krista/OneDrive - Umich/all_scored_grooming_20210112.csv')

g = sns.catplot(data=grooming_summary_df[grooming_summary_df["trial measure"].isin(["num_bouts", "num_interrupted_bouts"])],
                kind='bar',
                x="trial measure",
                y="value",
                hue='genotype',
                palette=palette,
                legend=False)
g.ax.set_xticklabels(["All Bouts", "Interrupted Bouts"])
g.ax.set(xlabel='', ylabel="Number of Bouts")
g.ax.set_title(f'Grooming Bouts by Genotype')
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('num_bouts.jpeg')), bbox_inches='tight')
plt.close()

#############

g1 = sns.catplot(data=grooming_summary_df[grooming_summary_df["trial measure"].isin(["num_chains", "num_complete_chains"])],
                kind='bar',
                x="trial measure",
                y="value",
                hue='genotype',
                palette=palette,
                legend=False)
g1.ax.set_xticklabels(["All Chains", "Complete Chains"])
g1.ax.set(xlabel='', ylabel="Number of Chains")
g1.ax.set_title(f'Grooming Chains by Genotype')
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('num_chains.jpeg')), bbox_inches='tight')
plt.close()

#############

g2 = sns.catplot(data=grooming_summary_df[grooming_summary_df["trial measure"].isin(["latency_to_onset"])],
                 kind='bar',
                 x="trial measure",
                 y="value",
                 hue='genotype',
                 palette=palette,
                 legend=False
                 )
g2.ax.set_xticklabels(["Latency to Onset"])
g2.ax.set(xlabel='', ylabel="Seconds")
g2.ax.set_title(f'Grooming Latency to Onset by Genotype')
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('latency_to_onset.jpeg')), bbox_inches='tight')
plt.close()

#############

g3 = sns.catplot(data=grooming_summary_df[grooming_summary_df["trial measure"].isin(["total_time_grooming"])],
                 kind='bar',
                 x="trial measure",
                 y="value",
                 hue='genotype',
                 palette=palette,
                 legend=False
                 )
g3.ax.set_xticklabels(["Total Time Grooming"])
g3.ax.set(xlabel='', ylabel="Seconds")
g3.ax.set_title(f'Grooming Time by Genotype')
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('total_time_grooming.jpeg')), bbox_inches='tight')
plt.close()