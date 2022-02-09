import database_pkg as dbpkg
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd


def simple_genotype(in_genotype):
    if in_genotype == "Dlx-CKO Control":
        return "control"
    elif in_genotype == "control":
        return in_genotype
    return "Dlx-CKO"


cap_size = 4
cap_thick = 1.5
err_line_width = 1.5
line_width = 1.5
w = 4

color_dict = {"Dlx-CKO Control": "#005AB5",
              "Dlx-CKO": "#DC3220"}

experiment = dbpkg.Experiment.get_by_name('dlxCKO-skilled-reaching')
scored_trials = experiment.get_all_scored_trials()
scored_trials = scored_trials.loc[scored_trials['session_num']<=21]
scored_trials
participated_trials = scored_trials.loc[(scored_trials['reach_score'] >= 1) & (scored_trials['reach_score']<=5)]
participated_trials
# all_mouse_trials_per_session = []
#
# for eartag in participated_trials.eartag.unique():
#     mouse_trials = participated_trials.loc[participated_trials['eartag']==eartag]
#     genotype = simple_genotype(mouse_trials.genotype.unique()[0])
#     trials_per_session = mouse_trials.value_counts(mouse_trials['session_num']).sort_index().reset_index().rename(columns={"session_num": "training day", 0: "# trials"})
#     trials_per_session['genotype'] = genotype
#     trials_per_session['eartag'] = eartag
#
#     all_mouse_trials_per_session.append(trials_per_session.to_dict())
#
#     ax = plt.subplot2grid((1, 1), (0, 0))
#     sns.pointplot(ax=ax, x="training day", y="# trials", data=trials_per_session)
#     ax.set_xlim([-1, 21])
#     ax.set_xticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
#     ax.set_xticklabels([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
#     ax.set_ylim([0, 225])
#
#     plt.tight_layout()
#     plt.savefig(f"/Users/Krista/Desktop/numTrials/byMouse/{genotype}_{eartag}.pdf")
#     plt.close()
#
trials_per_mouse_per_session = participated_trials.groupby(["session_dir", "session_num", "genotype"]).size().reset_index()
agg_trials_per_session = trials_per_mouse_per_session.groupby(["session_num", "genotype"]).agg([pd.DataFrame.mean, pd.DataFrame.sem]).reset_index()

fig = plt.figure()
fig.set_figwidth(w)
fig.set_dpi(1000)
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['font.sans-serif'] = "Arial"
plt.rcParams['xtick.major.pad'] = -0.5
plt.rcParams['ytick.major.pad'] = -0.5


ax = plt.subplot2grid((1, 1), (0, 0))

sns.lineplot(ax=ax, x="session_num", y=0,
             data=trials_per_mouse_per_session,
             hue='genotype', hue_order=["Dlx-CKO Control", "Dlx-CKO"], palette=color_dict,
             legend=True,
             linewidth=line_width,
             errorbar="se", err_style="bars",
             err_kws={'capsize': cap_size, 'capthick': cap_thick, 'elinewidth': err_line_width}
             )
ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
ax.set(xlabel='training day', ylabel="# trials")
labels = ['control', 'Dlx-CKO']
ax.legend(title=None, labels=labels)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(f"/Users/Krista/Desktop/numTrials/all_mice.pdf")
plt.close('all')
