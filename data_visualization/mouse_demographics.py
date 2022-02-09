import database_pkg as dbpkg
import pandas as pd

participants = pd.read_sql(dbpkg.db.session.query(dbpkg.Mouse.mouse_id,
                                                     dbpkg.Mouse.eartag,
                                                     dbpkg.Mouse.sex,
                                                     dbpkg.Mouse.birthdate,
                                                     dbpkg.Mouse.genotype,
                                                     dbpkg.ParticipantDetail.start_date,
                                                     dbpkg.ParticipantDetail.end_date,
                                                     dbpkg.ParticipantDetail.exp_spec_details,
                                                     dbpkg.Experiment.experiment_name) \
                              .join(dbpkg.ParticipantDetail, dbpkg.ParticipantDetail.mouse_id == dbpkg.Mouse.mouse_id) \
                              .join(dbpkg.Experiment, dbpkg.Experiment.experiment_id == dbpkg.ParticipantDetail.experiment_id) \
                              .statement,
                              dbpkg.db.session.bind)

age_at_experiment_start = [dbpkg.Date.as_date(start_date)-dbpkg.Date.as_date(birth_date) for idx, [mouse_id, eartag, sex, birth_date, genotype, start_date, end_date, exp_spec_details, experiment_name] in participants.iterrows()]
age_at_experiment_start = [days_obj.days for days_obj in age_at_experiment_start]

participants.insert(participants.shape[1], 'age_at_experiment_start',age_at_experiment_start)

participants.to_csv('/Users/Krista/Desktop/figures/mouse_demographics.csv')