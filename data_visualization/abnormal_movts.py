import database_pkg as dbpkg
import pandas as pd
from data_visualization.plot_functions import get_mean_sem, genotype_cleanup, Column, create_stacked_bar_chart, \
    format_ax

custom_colors = {'Dlx-CKO Control': "#005AB5", "Dlx-CKO": "#DC3220"}
experiment = dbpkg.Experiment.get_by_name('dlxCKO-skilled-reaching')

srScores_df = pd.read_sql(dbpkg.db.session.query(dbpkg.Mouse.mouse_id,
                                                 dbpkg.Mouse.eartag,
                                                 dbpkg.Mouse.sex,
                                                 dbpkg.Mouse.birthdate,
                                                 dbpkg.Mouse.genotype,
                                                 dbpkg.Session.session_id,
                                                 dbpkg.Session.session_date,
                                                 dbpkg.Session.session_dir,
                                                 dbpkg.Session.session_num,
                                                 dbpkg.SRTrialScore.trial_score_id,
                                                 dbpkg.SRTrialScore.trial_id,
                                                 dbpkg.SRTrialScore.reviewer_id,
                                                 dbpkg.SRTrialScore.reach_score,
                                                 dbpkg.SRTrialScore.abnormal_movt_score) \
                          .join(dbpkg.Session, dbpkg.Session.mouse_id == dbpkg.Mouse.mouse_id) \
                          .join(dbpkg.Trial, dbpkg.Trial.session_id == dbpkg.Session.session_id) \
                          .join(dbpkg.SRTrialScore, dbpkg.SRTrialScore.trial_id == dbpkg.Trial.trial_id) \
                          .statement,
                          dbpkg.db.session.bind)

duplicate_trials = srScores_df.trial_id[srScores_df.trial_id.duplicated(keep='first')]

krista = dbpkg.Reviewer.get_by_name('Krista', 'K')
alliC = dbpkg.Reviewer.get_by_name('Alli', 'C')
dan = dbpkg.Reviewer.get_by_name('Dan', 'L')

for trial_id in duplicate_trials.iteritems():
    duplicates = srScores_df[srScores_df.trial_id == trial_id[1]]

    keep = duplicates[duplicates.reviewer_id == krista.reviewer_id]
    if len(keep) == 0:
        keep = duplicates[duplicates.reviewer_id == alliC.reviewer_id]

    if len(keep) == 0:
        keep = duplicates[duplicates.reviewer_id == dan.reviewer_id]

    if len(keep) == 0:
        print('choose next preference')

    remove = duplicates[duplicates.trial_score_id != keep.trial_score_id.values[0]]
    for item in remove.iterrows():
        srScores_df.drop(item[0], inplace=True)

print('okay')

