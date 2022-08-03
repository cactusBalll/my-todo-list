
from datetime import datetime
from PyQt5.QtCore import QDateTime


def QDateTime2Pydatetime(src: 'QDateTime') -> 'datetime':
    """其实Qt框架的日期比Python标准库好用。。。"""
    date = src.date()
    t = src.time()
    return datetime(date.year(), date.month(), date.day(),
                    t.hour(), t.minute(), t.second())


def Pydatetime2QDateTime(src: 'datetime') -> 'QDateTime':
    return QDateTime(src.year, src.month, src.day,
                     src.hour, src.minute, src.second)
