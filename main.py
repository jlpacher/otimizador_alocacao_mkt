from input import possible_promotions, partners, mechanics, system_settings
from promo_scheduling.solver import MechanicPartnerAssignmentSolver

# parceiros > maquinas de produzir clientes
# mecanica > operação de produção de cliente
# cada parceiro tem uma produtividade diferente para cada mecanica
# maximizar o numero de clientes


def main():
    solver = MechanicPartnerAssignmentSolver(
        possible_promotions=possible_promotions,
        partners=partners,
        mechanics=mechanics,
        system_settings=system_settings
    )
    solver.run()
    solver.print_solution()
    solver.print_statistics()
    solver.export_model('gitignore_model.txt')


if __name__ == '__main__':
    main()
