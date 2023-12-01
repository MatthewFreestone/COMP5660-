
from typing import Tuple, List, Any
from linear_genotype import LinearGenotype
from stock_population_evaluation import multiobjective_population_evaluation

def write_red_data_log(filename: str, best_hypervolume: int, pareto_front_genes: List[List]):
    with open(filename, 'w') as f:
        f.write(f"{best_hypervolume}\n")
        f.write(f"{len(pareto_front_genes)}\n")
        f.write('\n'.join((str(g) for g in pareto_front_genes))+"\n")

def load_red_data_log(filename: str, **kwargs) -> Tuple[float, List[int]]:
    '''Load the data_log contained in the given filename

    Params:
    -------
    filename: str 
    kwargs: the problem config file, which is needed to re-evaluate pareto front solutions

    Returns:
    -------
    A tuple containing, in order,
    final_gen_hypervolume: The hypervolume for the last generation
    final_pareto_front: list of individuals on the final pareto front
    '''
    final_pareto_front = []
    final_gen_hypervolume = -1

    with open(filename, 'r') as f:
        final_gen_hypervolume = int(f.readline().strip())
        num_pareto = int(f.readline().strip())
        for _ in range(num_pareto):
            genes = eval(f.readline().strip())
            individual = LinearGenotype()
            individual.genes = genes
            final_pareto_front.append(individual)

    # retrieve info on pareto front
    multiobjective_population_evaluation(final_pareto_front, **kwargs)

    return final_gen_hypervolume, final_pareto_front
