
import copy
from typing import List, Tuple, Union
from datetime import date, datetime, timedelta


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

        # 被任务调度分配的起止时间
        self.running_start_time = None
        self.running_end_time = None

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

    hint = {
        ONCE: '一次',
        PER_DAY: '每日',
        PER_WEEK: '每周',
        PER_MONTH: '每月',
    }

    def __init__(self, cycle: int,
                 task: 'Task') -> None:
        self.cycle = cycle  # 触发描述，每周周几？每月几号？
        self.task = task  # 用于周期创建的任务模板

    def get_trigger_description_str(self) -> str:
        return Trigger.hint[self.cycle]

    def generate_task(self, d: date) -> Task:
        """如果当前日期应该生成一个Task,则生成,否则返回空"""
        delta_time = self.task.deadline - self.task.start_time
        ret = copy.deepcopy(self.task)
        ret.start_time = datetime(
            d.year, d.month, 
            d.day, self.task.start_time.hour,
            self.task.start_time.minute
            )
        ret.deadline = ret.start_time + delta_time
        if self.cycle == Trigger.PER_DAY:
            return ret
        if self.cycle == Trigger.PER_WEEK:
            if self.task.start_time.weekday() == d.weekday():
                return ret
        if self.cycle == Trigger.PER_MONTH:
            if self.task.start_time.day == d.day:
                return ret

        return None


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

    @staticmethod
    def get_empty_trigger() -> Trigger:
        return Trigger(Trigger.PER_DAY, TaskBuilder.get_empty_task())
