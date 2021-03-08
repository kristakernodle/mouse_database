import os
from pathlib import Path
from random import sample

import cv2
import numpy as np
import pandas as pd
from sqlalchemy import exists, and_
import time
import subprocess

from database_pkg import (Experiment, Reviewer, Session, Folder, BlindFolder, )
from database_pkg.blind_review import copy_blind_folder


def file_num_dict(session_files):
    out_dict = {}
    for file in session_files:
        file_num = file.stem.split('_')[-1].strip('Reaches')
        out_dict[file_num] = file
    return out_dict


def LED(cap, frame_number):
    # This function checks whether a blue LED is on
    # lower_blue and upper_blue provide the hsv upper and lower limits for detection

    cap.set(1, frame_number)
    ret, frame = cap.read()

    if ret is True:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([80, 143, 220])
        upper_blue = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        value = sum(sum(mask))
    else:
        value = 0

    return value


def isFirstFrame(frame_number, cap, secs, first_frame):
    # This function identifies the first frame in the video where an LED is on
    # Note: Assumtion is made that the frame rate is >= 59 fps

    testFrame = np.floor(frame_number - (60 * secs))
    value = LED(cap, testFrame)
    value_thresh = 9000
    if value > value_thresh and secs == 5:
        secs = 5
        frame_number = testFrame
    elif value > value_thresh and secs < 5:
        frame_number = testFrame
    elif value <= value_thresh and secs > 0.059:
        secs = 0.5 * secs
    elif value <= value_thresh and secs <= 0.059:
        first_frame = True
    else:
        print('something odd is happening')
        print('value %d', value)
        print('sec %d', secs)
        print('frame_number %d', frame_number)
        print('testFrame %d', testFrame)

    return [first_frame, frame_number, secs]


def LEDDetection(video_path):
    # This function reads in the video and performs the LED detection for a blinking LED.
    #
    # INPUT
    #   video_path  : PosixPath directory of video to be processed
    #
    # OUTPUT
    #   csv_path    : List containing all frame numbers that have been identified as the
    #                 start of the LED on period
    csv_path = video_path.parent.joinpath(f"{video_path.stem}.csv")
    cap = cv2.VideoCapture(str(video_path))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    trial_num = 0

    frame_num = 0

    vid_frames = []
    value_thresh = 9000
    while frame_num < frame_count:
        value = LED(cap, frame_num)
        if value > value_thresh:
            # If the LED is on:
            # Algorithm to test if we have the first frame

            if frame_num <= 1:
                first_frame = True
            else:
                first_frame = False

            secs = 5

            while first_frame is False:
                [first_frame, frame_num, secs] = isFirstFrame(frame_num, cap, secs, first_frame)

            trial_num += 1
            vid_frames.append({'trial': trial_num,
                               'frame': frame_num})

            frame_num = frame_num + 1400

        else:
            frame_num = frame_num + 300
            continue

    vid_frames_df = pd.DataFrame.from_records(vid_frames)
    vid_frames_df.to_csv(csv_path)

    cap.release()
    cv2.destroyAllWindows()

    return csv_path


def trim_video_to_trials(experiment, video_path, csv_path_obj):

    _, _, video_number = video_path.stem.split('_')
    folder_path = csv_path_obj.parent.joinpath(experiment.folder_re.replace('*', video_number))

    folder = Folder.query.filter_by(folder_dir=str(folder_path)).first()
    if folder_path.exists() and folder is not None:
        trials_to_trim = sorted([trial for trial in folder.trials if not Path(trial.trial_dir).exists()],
                                key=lambda t: t.trial_num)
        # TODO trim_one_video function implementation
    elif not folder_path.exists():
        folder_path.mkdir()

    cap = cv2.VideoCapture(str(video_path))
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_number_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    trial_frames = pd.read_csv(csv_path_obj,
                               usecols=['trial', 'frame'],
                               dtype={'trial': int, 'frame': int})

    # Loop through each trial to cut into short trial videos
    for idx, trial_info in trial_frames.iterrows():
        trial_number = trial_info.trial
        frame_number = trial_info.frame
        if len(str(trial_number)) < 2:
            trial_number = f"0{trial_number}"
        else:
            trial_number = f"{trial_number}"

        if frame_number + 1080 > total_number_frames:
            end_frame = total_number_frames
        else:
            end_frame = frame_number + 1080

        trial_path = folder_path.joinpath(f"{csv_path_obj.stem}_R{trial_number}.mp4")

        os.chdir(trial_path.parent)

        subprocess.call(
            [
                "ffmpeg",
                "-i",
                str(video_path),
                "-ss",
                time.strftime('%H:%M:%S', time.gmtime(round(frame_number / frame_rate, 2))),
                "-to",
                time.strftime('%H:%M:%S', time.gmtime(round(end_frame / frame_rate, 2))),
                "-c:v",
                "copy",
                "-an",
                str(trial_path)
            ]
        )
        if trial_path.exists():
            continue
        else:
            return False
    return True


def blind_review_full_processing(experiment_name='dlxCKO-chatSap-skilled-reaching', reviewer_name='Alli C', num_sessions=1):
    experiment = Experiment.get_by_name(experiment_name)
    first_name, last_name = reviewer_name.split(' ')
    reviewer = Reviewer.query.filter_by(first_name=first_name, last_name=last_name).first()

    # All sessions not blinded
    all_sessions_no_blind_folders = Session.query.filter(Session.experiment_id == experiment.experiment_id).filter(
        ~exists().where(and_(Session.session_id == Folder.session_id,
                             Folder.folder_id == BlindFolder.folder_id,
                             ))).all()


    sessions_to_process = sample(all_sessions_no_blind_folders, num_sessions)

    for session in all_sessions_no_blind_folders:

        if 'MISSINGDATA' in session.session_dir:
            continue

        # Check if the number of session videos is equal to the number of processed folders
        session_videos = list(Path(session.session_dir).glob('*.MP4'))
        session_folders = list(Path(session.session_dir).glob(experiment.folder_re))
        all_csv = list(Path(session.session_dir).glob('*.csv'))
        session_csv = [item for item in all_csv if 'Scored' not in item.stem]

        video_num_dict = file_num_dict(session_videos)
        csv_num_dict = file_num_dict(session_csv)
        folder_num_dict = file_num_dict(session_folders)
        combined_num_dict = {x: (video_num_dict.get(x), csv_num_dict.get(x), folder_num_dict.get(x))
                             for x in set(video_num_dict).union(csv_num_dict).union(folder_num_dict)}

        for file_num in combined_num_dict.keys():
            video_path, folder_path, csv_path = combined_num_dict[file_num]

            # CASE DOES NOT EXIST
            #   video_path is None,       folder_path is None,        csv_path is None
            # DOWNLOAD VIDEOS
            #   video_path is None,       folder_path is None,        csv_path is not None
            # VIDEO CHOPPING, BLINDING
            #   video_path is not None,       folder_path is None,        csv_path is not None
            # LED DETECTION, VIDEO CHOPPING, BLINDING
            #   video_path is not None,       folder_path is None,        csv_path is None
            #   video_path is not None,       folder_path is not None,    csv_path is None
            # CHECK IF FOLDER IS IN DATABASE, CHECK BLINDING
            #   video_path is None,       folder_path is not None,    csv_path is None
            #   video_path is None,       folder_path is not None,    csv_path is not None
            #   video_path is not None,       folder_path is not None,    csv_path is not None

            if video_path is None and folder_path is None and csv_path is None:
                breakpoint()
            elif video_path is None and folder_path is None:
                print(f'download {session.session_dir}')
                continue
            elif video_path is not None and folder_path is None and csv_path is not None:

                # Cut video into trials
                success = trim_video_to_trials(experiment, video_path, csv_path)

                if success:
                    # Add folder and trials to database
                    folder = Folder.query.filter_by(folder_dir=str(folder_path)).first()
                    if folder is None:
                        Folder(session_id=session.session_id,
                               folder_dir=str(folder_path),
                               original_video=str(video_path),
                               trial_frame_number_file=str(csv_path)).add_to_db()
                        folder = Folder.query.filter_by(folder_dir=str(folder_path)).first()
                    folder.add_trials_from_dir(experiment.trial_re, session)

                    # Create a blind folder
                    blind_folder = folder.create_blind_folder(reviewer)
                    copy_blind_folder(reviewer, blind_folder)
                    continue
                else:
                    print('what vid chopping did not work')
            elif video_path is not None and csv_path is None:
                # perform LED detection
                csv_path = LEDDetection(video_path)
                success = trim_video_to_trials(experiment, video_path, csv_path)

                folder_path = csv_path.parent.joinpath(experiment.folder_re.replace('*', file_num))
                if success:
                    # Add folder and trials to database
                    folder = Folder.query.filter_by(folder_dir=str(folder_path)).first()
                    if folder is None:
                        Folder(session_id=session.session_id,
                               folder_dir=str(folder_path),
                               original_video=str(video_path),
                               trial_frame_number_file=str(csv_path)).add_to_db()
                        folder = Folder.query.filter_by(folder_dir=str(folder_path)).first()
                    folder.add_trials_from_dir(experiment.trial_re, session)

                    # Create a blind folder
                    blind_folder = folder.create_blind_folder(reviewer)
                    copy_blind_folder(reviewer, blind_folder)
                    continue
                else:
                    print('what vid chopping did not work')
            else:
                folder = Folder.query.filter_by(folder_dir=str(folder_path)).first()
                if folder is None:
                    Folder(session_id=session.session_id,
                           folder_dir=str(folder_path),
                           original_video=str(video_path),
                           trial_frame_number_file=str(csv_path)).add_to_db()
                    folder = Folder.query.filter_by(folder_dir=str(folder_path)).first()
                    folder.add_trials_from_dir(experiment.trial_re, session)

                    # Create a blind folder
                    blind_folder = folder.create_blind_folder(reviewer)
                    copy_blind_folder(reviewer, blind_folder)

                blind_folder = BlindFolder.query.filter_by(folder_id=folder.folder_id, reviewer_id=reviewer.reviewer_id).first()
                if blind_folder is None:
                    # Create a blind folder
                    blind_folder = folder.create_blind_folder(reviewer)
                    copy_blind_folder(reviewer, blind_folder)
                elif Path(reviewer.toScore_dir).joinpath(blind_folder.blind_name).exists() \
                        or Path(reviewer.scored_dir).joinpath(
                            f'{blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv').exists():
                    continue


if __name__ == '__main__':
    blind_review_full_processing()
