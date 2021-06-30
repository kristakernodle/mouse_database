import datetime
from pathlib import Path
import random
import string


class Date:
    def __init__(self, yyyymmdd):
        yyyymmdd = str(yyyymmdd).split('-')
        if len(yyyymmdd) == 1:
            yyyymmdd = yyyymmdd[0]
            self.year = int(yyyymmdd[0:4])
            self.month = int(yyyymmdd[4:6])
            self.day = int(yyyymmdd[6:])
        else:
            self.year = int(yyyymmdd[0])
            self.month = int(yyyymmdd[1])
            self.day = int(yyyymmdd[2])
        self.yyyymmdd = datetime.date(self.year, self.month, self.day).strftime('%Y%m%d')

    @classmethod
    def as_date(cls, yyyymmdd):
        date = cls(yyyymmdd)
        return datetime.date(date.year, date.month, date.day)

    def __str__(self):
        return self.yyyymmdd

    def __int__(self):
        return int(self.yyyymmdd)


def parse_date(in_date):
    try:
        datetime_obj = datetime.datetime.strptime(in_date, '%m/%d/%Y')
    except ValueError:
        datetime_obj = datetime.datetime.strptime(in_date, '%Y-%m-%d')
    return Date.as_date(datetime_obj.strftime('%Y%m%d'))


def check_if_sharedx_connected(sharedx_path='/Volumes/SharedX/Neuro-Leventhal/data'):
    if not Path(sharedx_path).exists():
        print(f"Connect SharedX to path: {sharedx_path} \n")
    return Path(sharedx_path).exists()


def exactly_one_true(in_list):
    if sum(list(map(int, in_list))) == 1:
        return True
    return False


def all_false(in_list):
    if sum(list(map(int, in_list))) == 0:
        return True
    return False


def get_original_video_and_frame_number_file(experiment, session, folder_dir):
    folder_dir = Path(folder_dir)
    folder_num = folder_dir.name.strip(experiment.folder_re.strip("*"))
    original_video_stem = '_'.join(Path(session.session_dir).name.strip('et').split('_')[:-1])
    original_video = Path(session.session_dir).joinpath(f"{original_video_stem}_{folder_num}.MP4")
    trial_frame_number_file = Path(session.session_dir).joinpath(f"{original_video_stem}_{folder_num}.csv")
    return original_video, trial_frame_number_file


def random_string_generator(len_string=10):
    """Generates a random string of length len_string.
    String will contain only lowercase letters and digits.
    :param len_string: length of returned string (default 10)
    :return: string of length len_string
    """

    lowercase_letters_and_digits = list(string.ascii_lowercase + string.digits)
    return ''.join(random.choices(lowercase_letters_and_digits, weights=None, k=len_string))


def convert_dict_keys_to_str(dict_in):
    dict_out = dict()
    for key in dict_in.keys():
        dict_out[str(key)] = dict_in[key]
    return dict_out


def merge_dicts(dict1, dict2, dict3):
    dict2.update(dict1)
    dict2.update(dict3)
    return dict2
