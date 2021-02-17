from random import sample
from sqlalchemy import exists, and_
from pathlib import Path
from .Models import (Experiment, Reviewer, Session, Folder, BlindFolder, Trial, )


def LEDDetection(video_path):
    video_frame_csv = None
    return video_frame_csv


def trim_video_to_trials(original_video):
    pass


def blind_review_full_processing(experiment_name='dlxCKO-skilled-reaching', reviewer_name='Krista K', num_sessions=1):
    experiment = Experiment.get_by_name(experiment_name)
    first_name, last_name = reviewer_name.split(' ')
    reviewer = Reviewer.query.filter_by(first_name=first_name, last_name=last_name)

    # All sessions not blinded
    all_sessions_no_blind_folders = Session.query.filter(Session.experiment_id == experiment.experiment_id).filter(
        ~exists().where(and_(Session.session_id == Folder.session_id,
                             Folder.folder_id == BlindFolder.folder_id,
                             ))).all()

    sessions_to_process = sample(all_sessions_no_blind_folders, num_sessions)

    for session in all_sessions_no_blind_folders:

        # Check if the number of session videos is equal to the number of processed folders
        session_videos = list(Path(session.session_dir).glob('*.MP4'))
        session_folders = list(Path(session.session_dir).glob(experiment.folder_re))
        all_csv = list(Path(session.session_dir).glob('*.csv'))
        session_csv = [item for item in all_csv if 'Scored' not in item.stem]

        nonzero_session_folders = (len(session.folders) > 0)
        session_folder_for_each_video = (len(session_folders) == len(session_videos))
        session_csv_for_each_video = (len(session_csv) == len(session_videos))
        session_folders_in_db = (len(session.folders) == len(session_folders))
        session_csv_for_each_folder = len(session_csv) == len(session.folders)

        if ('MISSINGDATA' in session.session_dir):
            continue
        elif (not nonzero_session_folders) and session_folder_for_each_video:
            # These folders need to be added to the database
            experiment._update_folders()
            experiment._update_trials()

        elif (len(session_videos) == 0 and len(session_csv) == 0) \
                or (len(session_csv) != 0 and len(session_videos) == 0 and len(session_folders) == 0):
            # These videos need to be downloaded from the cloud
            case = 0
        elif (not session_csv_for_each_video) and len(session_videos) > 0:
            # These videos need to have LED detection performed
            case = 1
        elif session_csv_for_each_video and (not session_folder_for_each_video):
            # These videos need to be chopped
            case = 2
        elif session_csv_for_each_video and session_folder_for_each_video and session_folders_in_db \
                or (len(session_videos) == 0 and session_csv_for_each_folder):
            # If it looks like all videos have been analyzed (i.e., a csv file exists for each video)
            #   and all trials have been cut (i.e., a folder exists for each video):
            #   check each folder to make sure all trial videos exist.
            #       If any trial videos do not exist, begin trimming new trials from the original video file
            for folder in session.folders:
                if any([not Path(trial.trial_dir).exists() for trial in folder.trials]):
                        trim_video_to_trials(folder.original_video)
        else:
            print('what')


        #
        #
        # if ~nonzero_session_folders and session_folder_for_each_video:
        #     experiment.update()
        #     session = Session.query.get(session.session_id)
        #
        # if ~session_folder_for_each_video:
        #     # LED Detection and/or video chopping has to be performed before creating blind folders
        #     for video in session_videos:
        #
        #
        # elif nonzero_session_folders and session_folder_for_each_video and session_folders_in_db:
        #     # LED detection AND video chopping complete, create blind folders only
        #     for folder in session.folders:
        #         folder.create_blind_folder(reviewer)


