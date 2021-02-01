from math import isnan
from pathlib import Path

import pandas as pd
from pandas.io.parsers import ParserError

from database_pkg import Experiment, Mouse, Reviewer, Session, Folder, Trial, BlindTrial, SRTrialScore, \
    GroomingSummary, Date
from database_pkg.utilities import get_original_video_and_frame_number_file
import shutil


def update_sessions(experiment):
    if not Path(experiment.experiment_dir).exists():
        print(f'Experiment directory does not exist: {experiment.experiment_dir}')

    for participant in experiment.participants:

        # if Mouse.query.get(participant.mouse_id).eartag == 749:
        #     continue

        sessions_search_dir = Path(participant.participant_dir)
        if len(experiment.session_re.split('/')) > 1:
            for item in experiment.session_re.split('/')[:-1]:
                sessions_search_dir = sessions_search_dir.joinpath(item)

        sessions_in_dir = list(str(session) for session in
                               list(sessions_search_dir.glob(f'{experiment.session_re.split("/")[-1]}')))

        for session_dir in sessions_in_dir:
            session = Session.query.filter_by(session_dir=str(session_dir)).first()
            if session is None:
                session_name = Path(session_dir).name

                if experiment.experiment_name == 'pasta-handling':
                    et_eartag, session_date, session_num = session_name.split('_')
                else:
                    et_eartag, session_date, calibration_num, session_num = session_name.split('_')

                Session(mouse_id=participant.mouse_id,
                        experiment_id=experiment.experiment_id,
                        session_date=Date.as_date(session_date),
                        session_dir=session_dir,
                        session_num=int(session_num.strip('T-MISNGDA'))).add_to_db()


def update_folders(experiment):
    all_sessions = experiment.sessions
    for session in all_sessions:
        all_folders = Path(session.session_dir).glob(f'{experiment.folder_re}')
        for folder_dir in all_folders:
            folder = Folder.query.filter_by(folder_dir=str(folder_dir)).first()
            if folder is None:
                original_video, trial_frame_number_file = get_original_video_and_frame_number_file(experiment,
                                                                                                   session,
                                                                                                   folder_dir)
                Folder(session_id=session.session_id,
                       folder_dir=str(folder_dir),
                       original_video=str(original_video),
                       trial_frame_number_file=str(trial_frame_number_file)).add_to_db()


def update_trials(experiment):

    for session in experiment.sessions:
        all_folders = session.folders

        if len(all_folders) == 0 and experiment.folder_re is None:
            print('This case is not solved')
            exit()

        for folder in all_folders:
            all_trials = Path(folder.folder_dir).glob(f'{experiment.trial_re}')
            for trial_dir in all_trials:
                trial = Trial.query.filter_by(trial_dir=str(trial_dir)).first()

                if trial is None:
                    trial_name = trial_dir.stem
                    trial_num = trial_name.split('_')[-1].strip('RTG')
                    Trial(experiment_id=experiment.experiment_id,
                          session_id=session.session_id,
                          folder_id=folder.folder_id,
                          trial_dir=str(trial_dir),
                          trial_date=session.session_date,
                          trial_num=int(trial_num[1:])).add_to_db()


def update_trial_scores(experiment):
    for folder in experiment.folders:
        for blind_folder in folder.score_folders:
            reviewer = Reviewer.query.get(blind_folder.reviewer_id)
            scored_blind_folder_path = Path(reviewer.scored_dir).joinpath(
                f"{blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")

            if scored_blind_folder_path.exists():
                try:
                    all_blind_folder_scores = pd.read_csv(
                        scored_blind_folder_path,
                        usecols=['Trial', 'Score', 'Movement', 'Grooming'],
                        delimiter=',',
                        dtype={'Trial': float, 'Score': float, 'Movement': str, 'Grooming': str}
                    )
                except ParserError:
                    print(f"Reformat file {scored_blind_folder_path}")
                    shutil.move(str(scored_blind_folder_path), str(Path(reviewer.scored_dir).parent))
                    continue

                for index, scored_row in all_blind_folder_scores.iterrows():
                    if isnan(scored_row['Trial']) or isnan(scored_row['Score']):
                        continue

                    blind_trial = BlindTrial.query.filter_by(blind_folder_id=blind_folder.blind_folder_id,
                                                             blind_trial_num=int(scored_row['Trial'])).first()

                    if blind_trial is None:
                        blind_trial_num = int(scored_row['Trial'])
                        trial = Trial.query.filter_by(folder_id=folder.folder_id, trial_num=blind_trial_num).first()
                        if trial is None:
                            print('Trial is none?')
                            continue
                        blind_trial = BlindTrial(blind_folder_id=blind_folder.blind_folder_id,
                                                 reviewer_id=reviewer.reviewer_id,
                                                 trial_id=trial.trial_id,
                                                 folder_id=folder.folder_id,
                                                 blind_trial_num=blind_trial_num)
                        blind_trial.add_to_db()

                    if scored_row['Movement'] == '1':
                        movt = True
                    else:
                        movt = False

                    if scored_row['Grooming'] == '1':
                        groom = True
                    elif scored_row['Grooming'] == '0':
                        groom = False
                    else:
                        groom = None

                    trial_score = SRTrialScore.query.filter_by(trial_id=blind_trial.trial_id,
                                                               reviewer_id=reviewer.reviewer_id).first()

                    if trial_score is None:
                        if groom is None:
                            print('I guess we have to figure this out now')
                        SRTrialScore(trial_id=blind_trial.trial_id,
                                     reviewer_id=blind_trial.reviewer_id,
                                     reach_score=int(scored_row['Score']),
                                     abnormal_movt_score=movt,
                                     grooming_score=groom).add_to_db()
                    elif all([trial_score.reach_score == int(scored_row['Score']),
                              trial_score.abnormal_movt_score == movt,
                              trial_score.grooming_score == groom]):
                        continue
                    else:
                        trial_score.reach_score = int(scored_row['Score'])
                        trial_score.abnormal_movt_score = movt
                        trial_score.grooming_score = groom
                        trial_score.add_to_db()

            else:
                print(f"Not Scored: {str(scored_blind_folder_path)}")


def update_grooming_summary(experiment=Experiment.query.filter_by(experiment_name="grooming").first()):
    for session in experiment.sessions:
        session_dir = Path(session.session_dir)
        scored_session_dir = session_dir.parent.parent.joinpath('grooming_analysis_algorithm')\
            .joinpath(session_dir.parent.stem)\
            .joinpath(session_dir.stem)

        if not scored_session_dir.exists():
            continue

        score_sheet_path = list(scored_session_dir.glob('*.xlsx'))

        if len(score_sheet_path) != 1:
            continue
        else:
            score_sheet_path = score_sheet_path[0]

        score_sheet = pd.read_excel(score_sheet_path, engine='openpyxl', index_col=0).transpose()

        for item in score_sheet.index:
            if 'Trial' not in item:
                continue

            GroomingSummary(session_id=session.session_id,
                            scored_session_dir=str(score_sheet_path),
                            trial_num=int(item.strip('Trial')),
                            trial_length=score_sheet['Total session time (m)'][item],
                            latency_to_onset=score_sheet["Latency to grooming onset (s)"][item],
                            num_bouts=score_sheet["Number of Bouts"][item],
                            total_time_grooming=score_sheet["Total Time Grooming (s)"][item],
                            num_interrupted_bouts=score_sheet["Number of Interrupted Bouts"][item],
                            num_chains=score_sheet["Number of Chains"][item],
                            num_complete_chains=score_sheet["Number of Complete Chains"][item],
                            avg_time_per_bout=score_sheet["Average Time Per Bout (s)"][item]).add_to_db()


def update_pasta_handling_scores():
    pass
