
from typing import List, Tuple, Union
from datetime import datetime, timedelta


class Task:

    def __init__(self, title: str, description: str,
                 start_time: 'datetime',
                 deadline: 'datetime', timecost: int,
                 importance: int, trigger: 'Trigger',
                 category: List[str]) -> None:
        self.title = title
        self.description = description
        self.start_time = start_time
        self.deadline = deadline
        # timecost单位为小时
        self.timecost = timecost  # 可选的，如果没有指定，自动计划不可用
        self.importance = importance  # 0, 1, 2, 3
        self.trigger = trigger
        self.category = category
        self.completed = False
        self.deleted = False

    def is_active(self, date_range: Tuple['datetime', 'datetime']) -> bool:
        # 与设定时间段有交集
        return not (date_range[1] < self.start_time or date_range[0] > self.deadline)

    def has_tag(self, tag: str) -> bool:
        return tag in self.category

    def set_completed(self) -> None:
        self.completed = True

    def get_importance_str(a: int) -> str:
        if a == 0:
            return "无"
        if a == 1:
            return "不重要"
        if a == 2:
            return "一般重要"
        if a == 3:
            return "非常重要"
        return ""


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
        ret = Task(title, description, start_time,
                   dead_line, None, 0, None, None)
        return ret

    @staticmethod
    def get_empty_task() -> Task:
        """for test"""
        return Task(None, None, None, None, 0, 0, None, None)
