from dataclasses import dataclass
from ortools.sat.python import cp_model


@dataclass
class Partner:
    name: str


@dataclass
class Mechanic:
    name: str
    duration: int = 1


@dataclass
class Promotion:
    partner: Partner
    mechanic: Mechanic
    productivity: int


@dataclass
class Assignment:
    is_active: cp_model.IntVar
    promotion: Promotion
