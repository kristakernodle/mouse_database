import pandas as pd
import json
from pathlib import Path

from database_pkg import db, Date, Mouse, Reviewer, Experiment, ParticipantDetail


def populate_mouse_from_file(full_path):
    mouse_data_frame = pd.read_csv(full_path, delimiter=',', dtype={'mouse_id': str, 'eartag': int,
                                                                    'birthdate': str, 'genotype': bool,
                                                                    'sex': str})
    for index, mouse_row in mouse_data_frame.iterrows():
        if Mouse.query.get(mouse_row["mouse_id"]) is None:
            db.session.add(
                Mouse(mouse_id=mouse_row["mouse_id"], eartag=mouse_row["eartag"],
                      birthdate=Date.as_date(mouse_row["birthdate"]), genotype=mouse_row["genotype"],
                      sex=mouse_row["sex"])
            )
            db.session.commit()


def populate_reviewers_from_file(full_path):
    reviewer_data_frame = pd.read_csv(full_path, delimiter=',', dtype={'reviewer_id': str, 'first_name': str,
                                                                       'last_name': str, 'toscore_dir': str,
                                                                       'scored_dir': str})
    for index, reviewer_row in reviewer_data_frame.iterrows():
        if Reviewer.query.get(reviewer_row["reviewer_id"]) is None:
            db.session.add(
                Reviewer(reviewer_id=reviewer_row["reviewer_id"], first_name=reviewer_row["first_name"],
                         last_name=reviewer_row["last_name"], toScore_dir=reviewer_row["toscore_dir"],
                         scored_dir=reviewer_row["scored_dir"])
            )
            db.session.commit()


def populate_experiments_from_file(full_path):
    experiments_data_frame = pd.read_csv(full_path, delimiter=',', dtype={'experiment_id': str, 'experiment_dir': str,
                                                                          'experiment_name': str})
    for index, experiment_row in experiments_data_frame.iterrows():
        if Experiment.query.get(experiment_row["experiment_id"]) is None:
            db.session.add(
                Experiment(experiment_id=experiment_row["experiment_id"],
                           experiment_dir=experiment_row["experiment_dir"],
                           experiment_name=experiment_row["experiment_name"])
            )
            db.session.commit()


def populate_participant_details_from_file(full_path):
    participant_details_df = pd.read_csv(full_path, delimiter=',', dtype={'detail_id': str, 'mouse_id': str,
                                                                          'experiment_id': str, 'start_date': str,
                                                                          'end_date': str, 'participant_dir': str,
                                                                          'exp_spec_details': str})
    for index, detail_row in participant_details_df.iterrows():
        if any([Mouse.query.get(detail_row["mouse_id"]) is None,
               Experiment.query.get(detail_row["experiment_id"]) is None]):
            print('Mouse or experiment does not exist')
        elif ParticipantDetail.query.get(detail_row["detail_id"]) is None:

            if type(detail_row["exp_spec_details"]) is not str:
                exp_spec_details = None
            else:
                exp_spec_details = json.loads(detail_row["exp_spec_details"])
            db.session.add(
                ParticipantDetail(detail_id=detail_row["detail_id"], mouse_id=detail_row["mouse_id"],
                                  experiment_id=detail_row["experiment_id"],
                                  start_date=Date.as_date(detail_row["start_date"]),
                                  end_date=Date.as_date(detail_row["end_date"]),
                                  participant_dir=detail_row["participant_dir"],
                                  exp_spec_details=exp_spec_details)
            )
            db.session.commit()


def populate_experiment_from_experiment_dir(experiment_dir):
    experiment = Experiment.query.filter(Experiment.experiment_dir == experiment_dir).first()
    for participant in experiment.participant_detail:
        all_in_part_dir = Path(participant.participant_dir).glob('*')

