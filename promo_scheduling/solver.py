
from typing import Dict, List
from ortools.sat.python import cp_model

from entity import Assignment, Mechanic, Partner, Promotion


class MechanicPartnerAssignmentSolver:
    def __init__(self, possible_promotions: List[Promotion], partners: List[Partner], mechanics: List[Mechanic]) -> None:
        self.possible_promotions = possible_promotions
        self.partners = partners
        self.mechanics = mechanics
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.all_assignments: Dict[str, Assignment] = {}

    def create_variables_is_promotion_active(self):
        for promotion in self.possible_promotions:
            partner = promotion.partner
            mechanic = promotion.mechanic
            relation_id = f'{partner.name}_{mechanic.name}'
            is_promo_active = self.model.NewBoolVar('Promotion_' + relation_id)
            self.all_assignments[relation_id] = Assignment(is_promo_active, promotion)

    def add_constraint_max_one_promo_per_partner(self):
        for partner in self.partners:
            self.model.AddAtMostOne(
                self.all_assignments[f'{partner.name}_{mechanic.name}'].is_active
                for mechanic in self.mechanics)

    def add_constraint_max_one_partner_per_promo(self):
        for mechanic in self.mechanics:
            self.model.AddAtMostOne(
                self.all_assignments[f'{partner.name}_{mechanic.name}'].is_active
                for partner in self.partners)

    def create_objective_function(self):
        self.model.Maximize(
            sum(
                assignment.is_active * assignment.promotion.productivity * assignment.promotion.mechanic.duration
                for assignment in self.all_assignments.values()
            )
        )

    def run(self):
        self.create_variables_is_promotion_active()
        self.add_constraint_max_one_promo_per_partner()
        self.add_constraint_max_one_partner_per_promo()
        self.create_objective_function()
        self.status = self.solver.Solve(self.model)

    def print_solution(self):
        if self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE:
            print('Solution:')

            output = []
            for promotion in self.possible_promotions:
                partner = promotion.partner
                mechanic = promotion.mechanic
                is_active = self.solver.Value(
                    self.all_assignments[f'{partner.name}_{mechanic.name}'].is_active)
                if is_active:
                    output.append(
                        f"Parceiro {promotion.partner.name} "
                        f"com promoção {promotion.mechanic.name} "
                        f"resultando em {promotion.productivity * promotion.mechanic.duration} clientes")

            # Finally print the solution found.
            print(f'Optimal result: {self.solver.ObjectiveValue()} clientes')
            print('\n'.join(output))
        else:
            print('No solution found.')
