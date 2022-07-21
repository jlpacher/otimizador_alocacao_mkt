import collections
from dataclasses import dataclass
from typing import Dict
from ortools.sat.python import cp_model

# parceiros > maquinas de produzir clientes
# mecanica > operação de produção de cliente
# cada parceiro tem uma produtividade diferente para cada mecanica
# maximizar o numero de clientes


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


def main():
    dz_1 = Mechanic('DZ 1', 10)
    dz_4 = Mechanic('DZ 4')
    dz_8 = Mechanic('DZ 8')

    amz = Partner('Amazon')
    nike = Partner('Nike')
    acom = Partner('Americanas')
    suba = Partner('Submarino')

    amz_jobs = [
        Promotion(
            partner=amz,
            mechanic=dz_1,
            productivity=1000
        ),
        Promotion(
            partner=amz,
            mechanic=dz_4,
            productivity=3000
        ),
        Promotion(
            partner=amz,
            mechanic=dz_8,
            productivity=5000
        )
    ]
    nike_jobs = [
        Promotion(
            partner=nike,
            mechanic=dz_1,
            productivity=2000
        ),
        Promotion(
            partner=nike,
            mechanic=dz_4,
            productivity=5000
        ),
        Promotion(
            partner=nike,
            mechanic=dz_8,
            productivity=6000
        )
    ]
    acom_jobs = [
        Promotion(
            partner=acom,
            mechanic=dz_1,
            productivity=5000
        ),
        Promotion(
            partner=acom,
            mechanic=dz_4,
            productivity=10000
        ),
        Promotion(
            partner=acom,
            mechanic=dz_8,
            productivity=15000
        )
    ]

    suba_jobs = [
        Promotion(
            partner=suba,
            mechanic=dz_1,
            productivity=5000
        ),
        Promotion(
            partner=suba,
            mechanic=dz_4,
            productivity=10000
        ),
        Promotion(
            partner=suba,
            mechanic=dz_8,
            productivity=15000
        )
    ]

    possible_promotions = [*amz_jobs, *nike_jobs, *acom_jobs, *suba_jobs]
    partners = [amz, nike, acom, suba]
    promotions = [dz_1, dz_4, dz_8]

    # Create the model.
    model = cp_model.CpModel()

    all_assignments: Dict[str, Assignment] = {}

    for promotion in possible_promotions:
        partner = promotion.partner
        mechanic = promotion.mechanic
        relation_id = f'{partner.name}_{mechanic.name}'
        is_promo_active = model.NewBoolVar('Promo_' + relation_id)
        all_assignments[relation_id] = Assignment(is_promo_active, promotion)

    for partner in partners:
        model.AddAtMostOne(
            all_assignments[f'{partner.name}_{promotion.name}'].is_active
            for promotion in promotions)

    for promotion in promotions:
        model.AddAtMostOne(
            all_assignments[f'{partner.name}_{promotion.name}'].is_active
            for partner in partners)

    model.Maximize(
        sum(
            assignment.is_active * assignment.promotion.productivity * assignment.promotion.mechanic.duration
            for assignment in all_assignments.values()
        )
    )

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Solution:')

        output = []
        for promotion in possible_promotions:
            partner = promotion.partner
            mechanic = promotion.mechanic
            is_active = solver.Value(
                all_assignments[f'{partner.name}_{mechanic.name}'].is_active)
            if is_active:
                output.append(
                    f"Parceiro {promotion.partner.name} "
                    f"com promoção {promotion.mechanic.name} "
                    f"resultando em {promotion.productivity * promotion.mechanic.duration} clientes")

        # Finally print the solution found.
        print(f'Optimal result: {solver.ObjectiveValue()} clientes')
        print('\n'.join(output))
    else:
        print('No solution found.')


if __name__ == '__main__':
    main()
