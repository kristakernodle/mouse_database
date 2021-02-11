import database_pkg as dbpkg
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

save_dir = '/Users/Krista/OneDrive - Umich/grooming'

palette = {"Control": 'b', "Knock-Out": 'r'}

experiment = dbpkg.Experiment.query.filter_by(experiment_name="grooming").first()

# Analyses Here:
#   1. Total number of transitions by genotype
#   2. Average number of transitions by bout (total # transitions / # bouts) by genotype

grooming_data_by_bout = list()
for bout in experiment.grooming_bouts:

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
        'total_num_transitions': total_num_transitions,
        'num_incorrect_transitions': total_num_incorrect_transitions,
        'bout_complete': bout_complete,
        'bout_interrupted': bout_interrupted,
    })
