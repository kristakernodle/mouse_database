import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats

from database_pkg import Experiment, Session, Mouse

save_dir = '/Users/Krista/OneDrive - Umich/grooming'

palette = {"Control": 'b', "Knock-Out": 'r'}

experiment = Experiment.query.filter_by(experiment_name="dlxCKO-grooming").first()

grooming_summary_data = list()
for grooming_summary in experiment.scored_grooming:
    session = Session.query.get(grooming_summary.session_id)
    mouse = Mouse.query.get(session.mouse_id)

    new_row = {'eartag': mouse.eartag,
               'genotype': mouse.genotype,
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
                     'chains_perMin': grooming_summary.chains_perMin,
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

#####
# Statistics
#####

# total_time_grooming
total_time_grooming = grooming_summary_df[grooming_summary_df["trial measure"].isin(["total_time_grooming"])]
total_time_grooming_ctrl = total_time_grooming[total_time_grooming["genotype"].isin(['Dlx-CKO Control'])]
total_time_grooming_ko = total_time_grooming[total_time_grooming["genotype"].isin(['Dlx-CKO'])]
scipy.stats.ttest_ind(total_time_grooming_ctrl["value"], total_time_grooming_ko["value"])
# statistic=-2.944660374908921
# pvalue=0.0044608042191159585

# number of bouts
num_bouts = grooming_summary_df[grooming_summary_df["trial measure"].isin(["num_bouts"])]
num_bouts_ctrl = num_bouts[num_bouts["genotype"].isin(['Dlx-CKO Control'])]
num_bouts_ko = num_bouts[num_bouts["genotype"].isin(['Dlx-CKO'])]
scipy.stats.ttest_ind(num_bouts_ctrl["value"], num_bouts_ko["value"])
# statistic = -4.427789133665384
# pvalue = 3.6612545858308215e-05

# num_interrupted_bouts
num_interrupted_bouts = grooming_summary_df[grooming_summary_df["trial measure"].isin(["num_interrupted_bouts"])]
num_interrupted_bouts_ctrl = num_interrupted_bouts[num_interrupted_bouts["genotype"].isin(['Dlx-CKO Control'])]
num_interrupted_bouts_ko = num_interrupted_bouts[num_interrupted_bouts["genotype"].isin(['Dlx-CKO'])]
scipy.stats.ttest_ind(num_interrupted_bouts_ctrl["value"], num_interrupted_bouts_ko["value"])
# statistic=-3.733093678732508,
# pvalue=0.0003962439771403303

# number of chains
num_chains = grooming_summary_df[grooming_summary_df["trial measure"].isin(["chains_perMin"])]
num_chains_ctrl = num_chains[num_chains["genotype"].isin(['Dlx-CKO Control'])]
num_chains_ko = num_chains[num_chains["genotype"].isin(['Dlx-CKO'])]
scipy.stats.ttest_ind(num_chains_ctrl["value"], num_chains_ko["value"])
# statistic=-1.6899573859573047,
# pvalue=0.09575468997316709

# average time per bout (total grooming time / number of bouts)
avg_time_per_bout = grooming_summary_df[grooming_summary_df["trial measure"].isin(["avg_time_per_bout"])]
avg_time_per_bout_ctrl = avg_time_per_bout[avg_time_per_bout["genotype"].isin(['Dlx-CKO Control'])]
avg_time_per_bout_ko = avg_time_per_bout[avg_time_per_bout["genotype"].isin(['Dlx-CKO'])]
scipy.stats.ttest_ind(avg_time_per_bout_ctrl["value"], avg_time_per_bout_ko["value"])
# statistic=1.446324925945046
# pvalue=0.15281859207376577

# latency to onset
lat_onset = grooming_summary_df[grooming_summary_df["trial measure"].isin(["latency_to_onset"])]
lat_onset_ctrl = lat_onset[lat_onset["genotype"].isin(['Dlx-CKO Control'])]
lat_onset_ko = lat_onset[lat_onset["genotype"].isin(['Dlx-CKO'])]
scipy.stats.ttest_ind(lat_onset_ctrl["value"], lat_onset_ko["value"], nan_policy='omit')
# statistic=0.16380222606076492
# pvalue=0.870395105892021

# number of complete chains
num_complete_chains = grooming_summary_df[grooming_summary_df["trial measure"].isin(["num_complete_chains"])]
num_complete_chains_ctrl = num_complete_chains[num_complete_chains["genotype"].isin(['Dlx-CKO Control'])]
num_complete_chains_ko = num_complete_chains[num_complete_chains["genotype"].isin(['Dlx-CKO'])]
scipy.stats.ttest_ind(num_complete_chains_ctrl["value"], num_complete_chains_ko["value"])
# statistic=-0.4472135954999577,
# pvalue=0.6561850994594577

# trial_length
trial_length = grooming_summary_df[grooming_summary_df["trial measure"].isin(["trial_length"])]
trial_length_ctrl = trial_length[trial_length["genotype"].isin(['Dlx-CKO Control'])]
trial_length_ko = trial_length[trial_length["genotype"].isin(['Dlx-CKO'])]
scipy.stats.ttest_ind(trial_length_ctrl["value"], trial_length_ko["value"])
# statistic=-0.04963595921076173,
# pvalue=0.9605623990588141

# plotting starts

g = sns.catplot(data=grooming_summary_df[grooming_summary_df["trial measure"].isin(["num_bouts", "num_interrupted_bouts"])],
                kind='bar',
                x="trial measure",
                y="value",
                hue='genotype',
                palette=palette,
                legend=False)
g.ax.set_xticklabels(["All Bouts", "Interrupted Bouts"])
g.ax.set(xlabel='', ylabel="Number of Bouts")
g.ax.set_title(f'DlxGrooming Bouts by Genotype')
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('num_bouts.jpeg')), bbox_inches='tight')
plt.close()

#############

g1 = sns.catplot(data=grooming_summary_df[grooming_summary_df["trial measure"].isin(["chains_perMin", "num_complete_chains"])],
                kind='bar',
                x="trial measure",
                y="value",
                hue='genotype',
                palette=palette,
                legend=False)
g1.ax.set_xticklabels(["All Chains", "Complete Chains"])
g1.ax.set(xlabel='', ylabel="Number of Chains")
g1.ax.set_title(f'DlxGrooming Chains by Genotype')
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('chains_perMin.jpeg')), bbox_inches='tight')
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
g2.ax.set_title(f'DlxGrooming Latency to Onset by Genotype')
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
g3.ax.set_xticklabels(["Total Time DlxGrooming"])
g3.ax.set(xlabel='', ylabel="Seconds")
g3.ax.set_title(f'DlxGrooming Time by Genotype')
plt.legend(title='Genotype')
plt.savefig(str(Path(save_dir).joinpath('total_time_grooming.jpeg')), bbox_inches='tight')
plt.close()
