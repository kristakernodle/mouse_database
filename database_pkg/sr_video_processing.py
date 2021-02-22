from random import sample
from pathlib import Path, PosixPath

import cv2
from sqlalchemy import exists, and_
import ffmpeg

from database_pkg import (Experiment, Reviewer, Session, Folder, BlindFolder, Trial, )


def file_num_dict(session_files):
    out_dict = {}
    for file in session_files:
        file_num = file.stem.split('_')[-1].strip('Reaches')
        out_dict[file_num] = file
    return out_dict


def LEDDetection(video_path):
    video_frame_csv = None
    return video_frame_csv


def trim_video_to_trials(experiment, video_number, csv_path_obj):

    original_video = csv_path_obj.parent.joinpath(csv_path_obj.stem + '.MP4')
    folder_path = csv_path_obj.parent.joinpath(experiment.folder_re.replace('*', video_number))

    if folder_path.exists():
        folder = Folder.query.filter_by(folder_dir=folder_path).first()
        trials_to_trim = sorted([trial for trial in folder.trials if not Path(trial.trial_dir).exists()],
                                key=lambda t: t.trial_num)
        # TODO trim_one_video function implementation

    folder_path.mkdir()

    probe = ffmpeg.probe(str(original_video))
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    total_number_frames = int(video_stream['nb_frames'])

    with open(csv_path_obj) as f:
        trial_frames = f.read().splitlines()

    # Loop through each trial to cut into short trial videos
    for frame_number in trial_frames:
        trial_number = trial_frames.index(frame_number) + 1
        frame_number = int(frame_number)

        if len(str(trial_number)) < 2:
            trial_number = f"0{trial_number}"
        else:
            trial_number = f"{trial_number}"

        if frame_number + 960 > total_number_frames:
            end_frame = total_number_frames
        else:
            end_frame = frame_number + 960

        trial_path = folder_path.joinpath(f"{csv_path_obj.stem}_R{trial_number}.mp4")

        o_vid_stream = ffmpeg.input(str(original_video))
        # o_vid_stream = ffmpeg.trim(o_vid_stream, start=frame_number/60, end=(frame_number+960)/60, duration=16)
        o_vid_stream = ffmpeg.output(o_vid_stream, str(trial_path), **{'vsync': '0', 't': '16'})
        ffmpeg.run(o_vid_stream)

        # # Define the command that will be used for cutting the videos
        # command = "ffmpeg -hide_banner -loglevel panic -i " + str(csv_path_obj) \
        #           + " -vf select=" + '"' + "gte(n" + "\\" + "," + str(frame_number) + "),setpts=PTS-STARTPTS" + '"' + " -r 60 -c:v libx264 -frames:v " + str(
        #     frames_to_cut) + " -t 16 " + str(trial_path)
        # # Run the system command
        # os.system(command)
        #
        # # Increase the trial count
        # vidCnt += 1


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
            # These videos need to be downloaded from the cloud OR the sharedx drive is not connected
            case = 0
        elif (not session_csv_for_each_video) and len(session_videos) > 0:
            # These videos need to have LED detection performed
            case = 1
        elif session_csv_for_each_video and (not session_folder_for_each_video):
            # Check to see which videos have folders
            csv_num_dict = file_num_dict(session_csv)
            folder_num_dict = file_num_dict(session_folders)

            combined_num_dict = {x: (csv_num_dict.get(x), folder_num_dict.get(x))
                                 for x in set(csv_num_dict).union(folder_num_dict)}

            for video_num, paths in combined_num_dict.items():
                if None in paths:
                    trim_video_to_trials(experiment, video_num, paths[0])



            # These videos need to be chopped


            for folder in session.folders:
                trim_video_to_trials(experiment, session, folder)
        elif session_csv_for_each_video and session_folder_for_each_video and session_folders_in_db \
                or (len(session_videos) == 0 and session_csv_for_each_folder):
            # If it looks like all videos have been analyzed (i.e., a csv file exists for each video)
            #   and all trials have been cut (i.e., a folder exists for each video):
            #   check each folder to make sure all trial videos exist.
            #       If any trial videos do not exist, begin trimming new trials from the original video file
            # TODO this takes too long
            # for folder in session.folders:
            #     if any([not Path(trial.trial_dir).exists() for trial in folder.trials]):
            #             trim_video_to_trials(experiment, session, folder)

            continue
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

if __name__ == '__main__':
    blind_review_full_processing()
