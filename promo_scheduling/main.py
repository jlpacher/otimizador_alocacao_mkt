import collections
from dataclasses import dataclass
from ortools.sat.python import cp_model

# parceiros > maquinas de produzir clientes
# mecanica > operação de produção de cliente
# cada parceiro tem uma produtividade diferente para cada mecanica
# maximizar o numero de clientes


@dataclass
class Partner:
    name: str


@dataclass
class Promotion:
    name: str
    duration: int = 1


@dataclass
class PartnerPromotionProductivity:
    partner: Partner
    promotion: Promotion
    productivity: int


def main():
    dz_1 = Promotion('DZ 1')
    dz_4 = Promotion('DZ 4')
    dz_8 = Promotion('DZ 8')

    amz = Partner('Amazon')
    nike = Partner('Nike')
    acom = Partner('Americanas')

    amz_jobs = [
        PartnerPromotionProductivity(
            partner=amz,
            promotion=dz_1,
            productivity=1000
        ),
        PartnerPromotionProductivity(
            partner=amz,
            promotion=dz_4,
            productivity=3000
        ),
        PartnerPromotionProductivity(
            partner=amz,
            promotion=dz_8,
            productivity=5000
        )
    ]
    nike_jobs = [
        PartnerPromotionProductivity(
            partner=nike,
            promotion=dz_1,
            productivity=2000
        ),
        PartnerPromotionProductivity(
            partner=nike,
            promotion=dz_4,
            productivity=5000
        ),
        PartnerPromotionProductivity(
            partner=nike,
            promotion=dz_8,
            productivity=6000
        )
    ]
    acom_jobs = [
        PartnerPromotionProductivity(
            partner=acom,
            promotion=dz_1,
            productivity=5000
        ),
        PartnerPromotionProductivity(
            partner=acom,
            promotion=dz_4,
            productivity=10000
        ),
        PartnerPromotionProductivity(
            partner=acom,
            promotion=dz_8,
            productivity=15000
        )
    ]

    jobs = [*amz_jobs, *nike_jobs, *acom_jobs]

    # Create the model.
    model = cp_model.CpModel()
    duration_horizon = 1
    productivity_horizon = 100000

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start end interval')
    # Named tuple to manipulate solution information.

    all_promotions_duration = {}
    all_promotions_productivity = {}
    partners_to_promotions = collections.defaultdict(list)

    for job in jobs:
        partner = job.partner
        promotion = job.promotion
        duration = job.promotion.duration
        suffix = f'_{partner.name}_{promotion.name}'

        # time vars
        start_var = model.NewIntVar(0, duration_horizon, 'time_start' + suffix)
        end_var = model.NewIntVar(0, duration_horizon, 'time_end' + suffix)
        interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                            'time_interval' + suffix)
        all_promotions_duration[f'{partner.name}_{promotion.name}'] = task_type(
            start=start_var,
            end=end_var,
            interval=interval_var
        )
        partners_to_promotions[partner.name].append(interval_var)

        productivity = job.productivity
        # productivity var
        start_var = model.NewIntVar(0, productivity_horizon, 'prod_start' + suffix)
        end_var = model.NewIntVar(0, productivity_horizon, 'prod_end' + suffix)
        interval_var = model.NewIntervalVar(start_var, productivity, end_var,
                                            'prod_interval' + suffix)
        all_promotions_productivity[f'{partner.name}_{promotion.name}'] = task_type(
            start=start_var,
            end=end_var,
            interval=interval_var
        )

    # Create and add disjunctive constraints.
    for partner_name, partner_to_promotions in partners_to_promotions.items():
        print(f"Adding no overlap to {partner_name}")
        model.AddNoOverlap(partner_to_promotions)

    # Makespan objective.
    obj_var = model.NewIntVar(0, duration_horizon, 'makespan')
    model.AddMaxEquality(obj_var, [
        promo.end for promo in all_promotions_duration.values()
    ])
    model.Maximize(obj_var)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    assigned_task_type = collections.namedtuple('assigned_task_type',
                                                'start promotion duration')

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Solution:')
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)

        for job in jobs:
            partner = job.partner
            promotion = job.promotion
            assigned_jobs[partner.name].append(
                assigned_task_type(start=solver.Value(
                    all_promotions_duration[f'{partner.name}_{promotion.name}'].start),
                    promotion=promotion.name,
                    duration=promotion.duration))

        # Create per machine output lines.
        output = assigned_jobs

        # Finally print the solution found.
        print(f'Optimal Schedule Length: {solver.ObjectiveValue()}')
        print(output)
    else:
        print('No solution found.')

    # Statistics.
    print('\nStatistics')
    print('  - conflicts: %i' % solver.NumConflicts())
    print('  - branches : %i' % solver.NumBranches())
    print('  - wall time: %f s' % solver.WallTime())


if __name__ == '__main__':
    main()
