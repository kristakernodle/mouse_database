import datetime
from pathlib import Path


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
    datetime_obj = datetime.datetime.strptime(in_date, '%m/%d/%Y')
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
