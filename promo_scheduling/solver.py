
from typing import Dict, List
from ortools.sat.python import cp_model

from promo_scheduling.entity import Assignment, Mechanic, Partner, Promotion, SystemSettings

# Adicionar array de bool var para representar a duração da promoção
# adicionar restrição de que x[i] >= x[i+1] para garantir que a duração
# ocupará as primeiras posições do array
# usar a weighted sum para encontrar a produtividade


class MechanicPartnerAssignmentSolver:
    def __init__(
            self,
            possible_promotions: List[Promotion],
            partners: List[Partner],
            mechanics: List[Mechanic],
            system_settings: SystemSettings
    ) -> None:
        self.possible_promotions = possible_promotions
        self.partners = partners
        self.mechanics = mechanics
        self.system_settings = system_settings
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        # self.solver.parameters.log_search_progress = True
        self.all_assignments: Dict[str, Assignment] = {}

    def create_variables(self) -> None:
        duration_horizon = max(promotion.mechanic.availability for promotion in self.possible_promotions)
        for promotion in self.possible_promotions:
            partner = promotion.partner
            mechanic = promotion.mechanic
            relation_id = f'{partner.name}_{mechanic.name}'
            start_var = self.model.NewIntVar(0, duration_horizon, 'start_' + relation_id)
            end_var = self.model.NewIntVar(0, duration_horizon, 'end_' + relation_id)
            duration_var = self.model.NewIntVar(0, duration_horizon, 'duration_' + relation_id)
            interval_var = self.model.NewIntervalVar(start_var, duration_var, end_var,
                                                     'interval_' + relation_id)

            # we cant end a promotion after the availability
            self.model.Add(end_var <= partner.availability)
            duration_array = [self.model.NewBoolVar(
                f"duration_{relation_id}_ pos_{i}") for i in range(mechanic.availability)]
            self.model.Add(sum(duration_array) == duration_var)
            for pos in range(mechanic.availability - 1):
                self.model.Add(duration_array[pos] >= duration_array[pos + 1])

            self.all_assignments[relation_id] = Assignment(
                start_var,
                end_var,
                interval_var,
                duration_array,
                promotion
            )

    def add_constraint_max_one_promo_per_partner(self) -> None:
        for partner in self.partners:
            self.model.Add(
                sum(self.all_assignments[f'{partner.name}_{mechanic.name}'].interval.SizeExpr()
                    for mechanic in self.mechanics) <= partner.availability
            )
        # for partner in self.partners:
        #     self.model.Add(
        #         sum(
        #             sum(self.all_assignments[f'{partner.name}_{mechanic.name}'].duration_array)
        #             for mechanic in self.mechanics) <= partner.availability
        #     )

    def add_constraint_promo_max_duration(self) -> None:
        for mechanic in self.mechanics:
            self.model.Add(
                sum(self.all_assignments[f'{partner.name}_{mechanic.name}'].interval.SizeExpr()
                    for partner in self.partners) <= mechanic.availability
            )
        # for mechanic in self.mechanics:
        #     self.model.Add(
        #         sum(
        #             sum(self.all_assignments[f'{partner.name}_{mechanic.name}'].duration_array)
        #             for partner in self.partners) <= mechanic.availability
        #     )

    def add_constraint_min_duration(self) -> None:
        for assignment in self.all_assignments.values():
            self.model.Add(
                assignment.interval.SizeExpr() >= self.system_settings.min_duration
            ).OnlyEnforceIf(
                assignment.duration_array[0]
            )

    def add_constraint_no_overlapping_promotion(self):
        for partner in self.partners:
            self.model.AddNoOverlap(
                self.all_assignments[f'{partner.name}_{mechanic.name}'].interval
                for mechanic in self.mechanics
            )

    def create_objective_function(self) -> None:
        self.model.Maximize(
            sum(
                assignment.productivity()
                for assignment in self.all_assignments.values()
            )
        )

    def has_solution_found(self) -> bool:
        return self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE

    def run(self) -> None:
        self.create_variables()
        self.add_constraint_max_one_promo_per_partner()
        self.add_constraint_promo_max_duration()
        self.add_constraint_no_overlapping_promotion()
        self.add_constraint_min_duration()
        self.create_objective_function()
        self.status = self.solver.Solve(self.model)

    def print_solution(self) -> None:
        if self.has_solution_found():
            print('Solution:')

            output = []
            for promotion in self.possible_promotions:
                partner = promotion.partner
                mechanic = promotion.mechanic
                assignment = self.all_assignments[f'{partner.name}_{mechanic.name}']
                start_var = self.solver.Value(assignment.start)
                end_var = self.solver.Value(assignment.end)
                productivity = self.solver.Value(assignment.productivity())
                duration_array = [self.solver.Value(assignment.duration_array[i])
                                  for i in range(assignment.promotion.mechanic.availability)]
                print(duration_array)
                output.append(
                    f"Parceiro {promotion.partner.name} "
                    f"com promoção {promotion.mechanic.name} "
                    f"iniciando em {start_var} e "
                    f"terminando em {end_var} "
                    f"com resultando em {productivity} clientes")

            print(f'Optimal result: {self.solver.ObjectiveValue()} clientes')
            print('\n'.join(output))
        else:
            print('No solution found.')

    def print_statistics(self) -> None:
        print('\nStatistics')
        print('  - conflicts: %i' % self.solver.NumConflicts())
        print('  - branches : %i' % self.solver.NumBranches())
        print('  - wall time: %f s' % self.solver.WallTime())

    def export_model(self, filename) -> None:
        self.model.ExportToFile(filename)
