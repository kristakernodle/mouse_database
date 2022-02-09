import database_pkg as dbpkg
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd

color_dict = {"Dlx-CKO Control": "#005AB5",
              "Dlx-CKO": "#DC3220"}

experiment = dbpkg.Experiment.get_by_name('dlxCKO-skilled-reaching')
scored_trials = experiment.get_all_scored_trials()
scored_trials = scored_trials.loc[scored_trials['session_num']<=21]


