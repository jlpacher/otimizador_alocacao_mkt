from dataclasses import dataclass
from typing import List
from ortools.sat.python import cp_model


@dataclass
class SystemSettings:
    min_duration = 3


@dataclass
class Partner:
    name: str
    availability: int = 1


@dataclass
class Mechanic:
    name: str
    availability: int = 1


@dataclass
class Promotion:
    partner: Partner
    mechanic: Mechanic
    productivity_ref: int


class Schedule:
    # 2d matrix
    #     duration
    # [[0, 0 ,0 ,0 ,0], <- if set, start at day 0
    #  [0, 0 ,0 ,0 ,0], <- if set, start at day 1
    #  [1, 1 ,0 ,0 ,0], <- if set, start at day 2
    #  [0, 0 ,0 ,0 ,0], <- if set, start at day 3
    #  [0, 0 ,0 ,0 ,0]] <- if set, start at day 4
    # this example means a duration of 2 days, starting at day 2
    schedule_array: List[List[cp_model.IntVar]]

    def __init__(self, name, model: cp_model.CpModel, length):
        self.schedule_array = [
            [model.NewBoolVar(f'{name}_[{i},{j}]') for i in range(length)]
            for j in range(length)]

    def get_duration_array_at_day(self, day):
        return self.schedule_array[day]

    def get_day_flags_var(self):
        # return the first flag of the duration array
        return [duration[0] for duration in self.schedule_array]


@dataclass
class Assignment:
    id: str
    is_active: cp_model.IntVar
    not_is_active: cp_model.IntVar
    start: cp_model.IntVar
    end: cp_model.IntVar
    interval: cp_model.IntervalVar
    schedule: Schedule
    promotion: Promotion

    def productivity(self):
        prod_ref = self.promotion.productivity_ref
        ret = 0
        for starting_day, duration_array in enumerate(self.schedule.schedule_array):
            if starting_day == 0:
                continue
            coefs = []
            for i in range(len(duration_array)):
                if i == 0:
                    coefs.append(prod_ref * 1)
                elif i == 1:
                    coefs.append(prod_ref * 4)
                else:
                    coefs.append(prod_ref)
            ret += cp_model.LinearExpr.WeightedSum(duration_array, coefs)
        return ret
