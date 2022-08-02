from copy import copy
from typing import List
from .task import *


class User:
    def __init__(self, name:str) -> None:
        self.name = name
        self.tasks: List['Task'] = [] # 所有任务
        self.triggers: List['Trigger'] = [] # 任务触发，用于实现每日每周任务。
        self.tags: List[str] = [] # 已定义的tags
        self.history_tasks: List['Task'] = [] # 已失效的任务
        self.draft: List['Task'] = [] # 草稿 

    def add_task(self, task: 'Task') -> None:
        self.tasks.append(task)
    # filter_* 返回符合条件的
    def filter_task_day(self, date: datetime) -> List['Task']:
        ret = []
        for task in self.tasks:
            if task.is_active((date,date,)):
                ret.append(task)
        
        return ret

    def filter_task_week(self, week_of_date: datetime) -> List['Task']:
        ret = []
        weekday = week_of_date.date().weekday()
        delta_time0 = timedelta(weekday)
        delta_time1 = timedelta(6-weekday)
        date0 = week_of_date - delta_time0
        date1 = week_of_date + delta_time1
        for task in self.tasks:
            if task.is_active((date0,date1,)):
                ret.append(task)
        
        return ret

    def filter_task_month(self, month_of_date: datetime) -> List['Task']:
        ret = []
        one_day = timedelta(1)

        date0 = copy(month_of_date)
        while date0.month == month_of_date.month:
            date0 -= one_day
        date0 += one_day

        date1 = copy(month_of_date)
        while date1.month == month_of_date.month:
            date1 += one_day 
        date0 -= one_day

        for task in self.tasks:
            if task.is_active((date0,date1,)):
                ret.append(task)
        
        return ret

    def filter_task_tag(self, tag: str) -> List['Task']:
        ret = []

        for task in self.tasks:
            if task.has_tag(tag):
                ret.append(task)
        
        return ret

    def clear_completed(self) -> None:
        """把完成或被删除的任务放入历史任务中"""
        t = []
        for task in self.tasks:
            if task.completed or task.deleted:
                t.append(task)
        self.tasks = list(filter(lambda x: not x.completed, self.tasks))
        self.history_tasks.extend(t)
