from re import S
from typing import List, Tuple, Union
from datetime import datetime, timedelta


class Task:

    def __init__(self, title: str, description: str,
                 start_time: 'datetime',
                 deadline: 'datetime', timecost: 'timedelta',
                 importance: int, trigger: 'Trigger',
                 category: List[str]) -> None:
        self.title = title
        self.description = description
        self.start_time = start_time
        self.deadline = deadline
        self.timecost = timecost #  可选的，在
        self.importance = importance
        self.trigger = trigger
        self.category = category
        self.completed = False

    def is_active(self, date_range: Tuple['datetime','datetime']) -> bool:
        # 与设定时间段有交集
        return not (date_range[1] < self.start_time or date_range[0] > self.deadline)

    def has_tag(self, tag:str) -> bool:
        return tag in self.category

    def set_completed(self) -> None:
        self.completed = True

class Trigger:
    """
    任务触发条件，单次？每日？每周？
    """
    ONCE = 0
    PER_DAY = 1
    PER_WEEK = 2
    PER_MONTH = 3

    def __init__(self, trig_type: int,
                 cycle: int, first_time: 'datetime',
                 task: 'Task') -> None:
        self.trig_type = trig_type
        self.cycle = cycle  # 触发描述，每周周几？每月几号？
        self.first_time = first_time  # 首次触发时间
        self.task = task  # 用于周期创建的任务模板


class TaskBuilder:
    @staticmethod
    def get_simple_task(title: str, description: str,
                        start_time: 'datetime', dead_line: 'datetime'):
        ret = Task(title, description, start_time, dead_line, None, 0, None, None)
        return ret
    @staticmethod
    def get_empty_task() -> Task:
        """for test"""
        return Task(None,None,None,None,None,None,None,None)




