from dataclasses import dataclass
from typing import List
from ortools.sat.python import cp_model


@dataclass
class SystemSettings:
    min_duration: int = 3


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
        self.length = length
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
    duration: cp_model.IntVar
    interval: cp_model.IntervalVar
    schedule: Schedule
    promotion: Promotion

    def get_productivity_at(self, start_day, num_days_since_start):
        prod_ref = self.promotion.productivity_ref

        if start_day == 0:
            return 0
        if num_days_since_start == 0:
            return prod_ref * 0
        elif num_days_since_start == 1:
            return prod_ref * 0.5555
        elif num_days_since_start == 2:
            return prod_ref * 0.7788
        elif num_days_since_start == 3:
            return prod_ref * 0.9930
        elif num_days_since_start == 4:
            return prod_ref * 1.0000
        elif num_days_since_start == 5:
            return prod_ref * 0.5547
        elif num_days_since_start == 6:
            return prod_ref * 0.4201
        elif num_days_since_start == 7:
            return prod_ref * 0.2962
        else:
            return prod_ref

    def productivity(self):
        ret = 0
        for starting_day, duration_array in enumerate(self.schedule.schedule_array):
            coefs = []
            for num_days in range(len(duration_array)):
                productivity = self.get_productivity_at(
                    start_day=starting_day,
                    num_days_since_start=num_days
                )
                coefs.append(productivity)
            ret += cp_model.LinearExpr.WeightedSum(duration_array, coefs)
        return ret
