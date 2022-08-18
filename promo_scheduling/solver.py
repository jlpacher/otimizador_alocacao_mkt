
from typing import Dict, List
from ortools.sat.python import cp_model

from promo_scheduling.entity import (
    Assignment,
    Schedule,
    Mechanic,
    Partner,
    Promotion,
    SystemSettings)

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
            promo_availability = max(mechanic.availability, partner.availability)
            relation_id = f'{partner.name}_{mechanic.name}'
            start_var = self.model.NewIntVar(0, duration_horizon, 'start_' + relation_id)
            end_var = self.model.NewIntVar(0, duration_horizon, 'end_' + relation_id)
            duration_var = self.model.NewIntVar(0, duration_horizon, 'duration_' + relation_id)
            interval_var = self.model.NewIntervalVar(start_var, duration_var, end_var,
                                                     'interval_' + relation_id)
            is_active = self.model.NewBoolVar(relation_id + '_is_active')
            not_is_active = self.model.NewBoolVar(relation_id + '_not_is_active')
            self.model.Add(is_active + not_is_active == 1)

            schedule = Schedule(
                name=relation_id,
                model=self.model,
                length=promo_availability
            )
            # we cant end a promotion after the availability
            self.model.Add(end_var <= partner.availability)

            for day in range(promo_availability):
                duration_array = schedule.get_duration_array_at_day(day)
                day_flags = schedule.get_day_flags_var()
                # TODO: enforce the day_flags[start_var] == 1
                # self.model.Add(day_flags[start_var] == 1)
                self.model.AddMapDomain(var=start_var, bool_var_array=day_flags)
                self.model.Add

                # only one day active
                self.model.AddAtMostOne(day_flags)
                # enforce duration if day is active
                self.model.Add(sum(duration_array) == duration_var).OnlyEnforceIf(day_flags[day])
                # enforce the duration array is a vector with all ones in the beginning
                for pos in range(promo_availability - 1):
                    self.model.Add(duration_array[pos] >= duration_array[pos + 1])

            self.all_assignments[relation_id] = Assignment(
                id=relation_id,
                is_active=is_active,
                not_is_active=not_is_active,
                start=start_var,
                end=end_var,
                interval=interval_var,
                schedule=schedule,
                promotion=promotion
            )
        self.model.AddAtLeastOne([assignment.is_active for assignment in self.all_assignments.values()])

    def add_constraint_max_one_promo_per_partner(self) -> None:
        for partner in self.partners:
            self.model.Add(
                sum(self.all_assignments[f'{partner.name}_{mechanic.name}'].interval.SizeExpr()
                    for mechanic in self.mechanics) <= partner.availability
            )

    def add_constraint_promo_max_duration(self) -> None:
        for mechanic in self.mechanics:
            self.model.Add(
                sum(self.all_assignments[f'{partner.name}_{mechanic.name}'].interval.SizeExpr()
                    for partner in self.partners) <= mechanic.availability
            )

    def add_constraint_min_duration(self) -> None:
        for assignment in self.all_assignments.values():
            self.model.Add(
                assignment.interval.SizeExpr() >= self.system_settings.min_duration
            ).OnlyEnforceIf(
                assignment.is_active
            )
            self.model.Add(
                assignment.interval.SizeExpr() == 0
            ).OnlyEnforceIf(
                assignment.not_is_active
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
        status_map = {
            cp_model.UNKNOWN: 'UNKNOWN',
            cp_model.MODEL_INVALID: 'MODEL_INVALID',
            cp_model.FEASIBLE: 'FEASIBLE',
            cp_model.INFEASIBLE: 'INFEASIBLE',
            cp_model.OPTIMAL: 'OPTIMAL'
        }
        print(status_map[self.status])
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

                schedule_matrix = [
                    [self.solver.Value(duration_array[i]) for i in range(len(duration_array))]
                    for duration_array in assignment.schedule.schedule_array
                ]
                is_active = self.solver.Value(assignment.is_active)
                print(f"{assignment.id} is active={is_active}")
                for line in schedule_matrix:
                    print(line)
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
