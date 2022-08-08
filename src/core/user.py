from copy import copy
from typing import List
from .task import *


class User:
    def __init__(self, name: str) -> None:
        self.name = name
        self.tasks: List['Task'] = []  # 所有任务
        self.triggers: List['Trigger'] = []  # 任务触发，用于实现每日每周任务。
        self.tags: List[str] = []  # 已定义的tags
        self.history_tasks: List['Task'] = []  # 已失效的任务
        self.draft: List['Task'] = []  # 草稿

    def add_task(self, task: 'Task') -> None:
        self.tasks.append(task)
    # filter_* 返回符合条件的

    def filter_task_day(self, date: datetime, history=False) -> List['Task']:
        ret = []

        date0 = datetime(date.year,date.month,date.day,0,0)
        date1 = datetime(date.year,date.month,date.day,23,59)

        tasks = self.tasks
        if history:
            tasks = self.history_tasks

        for task in tasks:
            if task.is_active((date0, date1,)):
                ret.append(task)

        return ret

    def filter_task_week(self, week_of_date: datetime, history=False) -> List['Task']:
        ret = []
        weekday = week_of_date.date().weekday()
        delta_time0 = timedelta(weekday)
        delta_time1 = timedelta(6-weekday)
        date0 = week_of_date - delta_time0
        date1 = week_of_date + delta_time1

        tasks = self.tasks
        if history:
            tasks = self.history_tasks
            
        for task in tasks:
            if task.is_active((date0, date1,)):
                ret.append(task)

        return ret

    def filter_task_month(self, month_of_date: datetime, history=False) -> List['Task']:
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

        tasks = self.tasks
        if history:
            tasks = self.history_tasks

        for task in tasks:
            if task.is_active((date0, date1,)):
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
        self.tasks = list(
            filter(lambda x: not x.completed and not x.deleted, self.tasks))
        self.history_tasks.extend(t)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def auto_schedule_tasks(self, day_of_date: datetime) -> List['Task']:
        """根据空闲时间自动调度任务，仅排今日需要做的任务"""
        """
        对于今日必须截止的任务，优先安排, 最早截止时间优先
        对于截止时间不在今日的任务，如果当日还有空闲时间，则分配给其它任务
        
        如果当日截止的任务不能被完成，则直接舍去
        """

        tasks_today = self.filter_task_day(day_of_date, False)
        tasks_dead_today = [] # 今日截止的任务
        tasks_not_dead_today = [] # 不是今日截止的任务
        date_now = datetime.now()
        date_today_end = datetime(date_now.year, date_now.month, date_now.day, 23, 59)
        date_now_hour = date_now.hour
        ret = []
        for task in tasks_today:
            # 截止日期在今天 而且 未截止的任务
            if task.deadline.day == date_now.day and task.deadline > date_now:
                tasks_dead_today.append(task)
            else:
                tasks_not_dead_today.append(task)

        tasks_dead_today = sorted(tasks_dead_today, key= lambda t: t.deadline)
        tasks_not_dead_today = sorted(tasks_not_dead_today, key=lambda t: t.deadline)


        # 分配时间给今日截止的任务
        for task in tasks_dead_today:
            # 可以今日截止的话
            if date_now_hour + task.timecost <= 23:
                if datetime(date_now.year, date_now.month, date_now.day, date_now_hour + task.timecost, date_now.minute) <= task.deadline:
                    date_now_hour += task.timecost
                    ret.append(task)

        # 截止在今日而且做不完的任务直接给扔了zzzzz

        if date_now_hour < 23:
            # 如果剩余小时>=任务数
            if 24 - date_now_hour - 1 >= len(tasks_not_dead_today):
                # every_task_time = (24 - date_now.hour - 1) // len(tasks_dead_today)
                ret += tasks_not_dead_today
            #否则，最早截止时间优先
            else:
                remain_hour = 24 - date_now_hour - 1
                for i in range(remain_hour):
                    ret.append(tasks_not_dead_today[i])

        print("here here")
        for i in ret:
            print(i.title, i.deadline, sep=" endtime: ")
        return ret










