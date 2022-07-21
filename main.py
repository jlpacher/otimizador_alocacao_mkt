from promo_scheduling.input import possible_promotions, partners, mechanics
from promo_scheduling.solver import MechanicPartnerAssignmentSolver

# parceiros > maquinas de produzir clientes
# mecanica > operação de produção de cliente
# cada parceiro tem uma produtividade diferente para cada mecanica
# maximizar o numero de clientes


def main():
    solver = MechanicPartnerAssignmentSolver(
        possible_promotions=possible_promotions,
        partners=partners,
        mechanics=mechanics
    )
    solver.run()
    solver.print_solution()


if __name__ == '__main__':
    main()
