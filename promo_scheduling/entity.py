from dataclasses import dataclass
from typing import List
from numpy import promote_types
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


@dataclass
class Assignment:
    start: cp_model.IntVar
    end: cp_model.IntVar
    interval: cp_model.IntervalVar
    duration_array: List[cp_model.IntervalVar]
    promotion: Promotion

    def productivity(self):
        availability = self.promotion.mechanic.availability
        prod_ref = self.promotion.productivity_ref
        coefs = []
        for i in range(availability):
            if i == 0:
                coefs.append(prod_ref * 1)
            elif i == 1:
                coefs.append(prod_ref * 4)
            else:
                coefs.append(prod_ref)
        return cp_model.LinearExpr.WeightedSum(self.duration_array, coefs)
