import datetime


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
        self.yyyymmdd = yyyymmdd

    @classmethod
    def as_date(cls, yyyymmdd):
        date = cls(yyyymmdd)
        return datetime.date(date.year, date.month, date.day)

    def __str__(self):
        return self.yyyymmdd

    def __int__(self):
        return int(self.yyyymmdd)

