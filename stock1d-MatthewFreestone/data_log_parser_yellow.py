from typing import Tuple, List, Any
from linear_genotype import LinearGenotype
from stock_population_evaluation import multiobjective_population_evaluation
from snake_eyes import read_config


def write_data_log_yellow(filename: str, best_hypervolume: int, pareto_front_genes: List[List], data_log: List[Any]):
    with open(filename, 'w') as f:
        f.write(f"{best_hypervolume}\n")
        f.write(f"{len(pareto_front_genes)}\n")
        f.write('\n'.join((str(g) for g in pareto_front_genes))+"\n")
        f.write(f"{len(data_log)}\n")
        f.write('\n'.join(data_log))

def load_data_log_yellow(filename: str, **kwargs) -> Tuple[float, List[LinearGenotype], List[int], List[int], List[float], List[int], List[float], List[float], List[float], List[float]]:
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
    evals: a list of eval count at that data point
    max_lengths: local max length
    mean_lengths: local average length
    max_widths: local max width
    mean_widths: local average width
    min_edges: local min shared edges
    mean_edges: local average shared edges
    local_hypervolumes: local hypervolume
    '''
    all_data = []
    final_pareto_front = []
    final_gen_hypervolume = -1

    with open(filename, 'r') as f:
        final_gen_hypervolume = float(f.readline().strip())
        num_pareto = int(f.readline().strip())
        for _ in range(num_pareto):
            genes = eval(f.readline().strip())
            individual = LinearGenotype()
            individual.genes = genes
            final_pareto_front.append(individual)
        num_data_lines = int(f.readline().strip())
        for _ in range(num_data_lines):
            data = f.readline().strip().split()
            all_data.append(data)

    # retrieve info on pareto front
    multiobjective_population_evaluation(final_pareto_front, **kwargs)
    # Data Log is created like this:
    # gen_data = f"{base_ea.evaluations} {best_length} {mean_length} {best_width} {mean_width} {hypervolume}"

    evals = [int(x[0]) for x in all_data]
    max_lengths = [float(x[1]) for x in all_data]
    mean_lengths = [float(x[2]) for x in all_data]
    max_widths = [int(x[3]) for x in all_data]
    mean_widths = [float(x[4]) for x in all_data]
    min_edges = [float(x[5]) for x in all_data]
    mean_edges = [float(x[6]) for x in all_data]
    local_hypervolumes = [float(x[7]) for x in all_data]

    return final_gen_hypervolume, final_pareto_front, evals, max_lengths, mean_lengths, max_widths, mean_widths, min_edges, mean_edges, local_hypervolumes

def load_average_data_logs_yellow(filenames: List[str], config_filename:str) -> Tuple[float, List[LinearGenotype], List[int], List[int], List[float], List[int], List[float], List[float],  List[float], List[float]]:
    '''Load the data_logs from all the filenames, average their data for each column, and return best overall hypervolume

    Params:
    -------
    filenames: List of string filenames
    config_filename: The name of the config file used for evals 


    Returns:
    -------
    A tuple containing, in order,
    best_hypervolume: The best hypervolume across all runs
    best_pareto_front: The pareto front with that hypervolume 
    evals: a list of eval count at that data point
    average_max_lengths: local max length, averaged over runs
    average_mean_lengths: local average length, averaged over runs
    average_max_widths: local max width, averaged over runs
    average_mean_widths: local average width, averaged over runs
    average_max_edges: local max edges, averaged over runs
    average_mean_edges: local average edges,, averaged over runs
    average_local_hypervolumes: local hypervolume, averaged over runs
    '''

    config = read_config(config_filename, globals(), locals())

    overall_best_hypervolume = -1
    overall_best_pareto_front = None

    x_evals = None
    total_max_lengths = None
    total_mean_lengths = None
    total_max_widths = None
    total_mean_widths = None
    total_max_edges = None
    total_mean_edges = None
    total_local_hypervolumes = None

    run_count = len(filenames)

    for name in filenames:
        res = load_data_log_yellow(name, **config['problem'])
        final_gen_hypervolume, final_pareto_front, evals, max_lengths, mean_lengths, max_widths, mean_widths, max_edges, mean_edges, local_hypervolumes = res
        
        if overall_best_pareto_front is None:
            overall_best_hypervolume = final_gen_hypervolume
            overall_best_pareto_front = final_pareto_front
        elif final_gen_hypervolume > overall_best_hypervolume:
            overall_best_hypervolume = final_gen_hypervolume
            overall_best_pareto_front = final_pareto_front

        if x_evals is None:
            x_evals = evals

        if total_max_lengths is None:
            total_max_lengths = max_lengths
        else:
            for i, v in enumerate(max_lengths):
                total_max_lengths[i] += v

        if total_mean_lengths is None:
            total_mean_lengths = mean_lengths
        else:
            for i, v in enumerate(mean_lengths):
                total_mean_lengths[i] += v

        if total_max_widths is None:
            total_max_widths = max_widths
        else:
            for i, v in enumerate(max_widths):
                total_max_widths[i] += v

        if total_mean_widths is None:
            total_mean_widths = mean_widths
        else:
            for i, v in enumerate(mean_widths):
                total_mean_widths[i] += v

        if total_max_edges is None:
            total_max_edges = max_edges
        else:
            for i, v in enumerate(max_edges):
                total_max_edges[i] += v

        if total_mean_edges is None:
            total_mean_edges = mean_edges
        else:
            for i, v in enumerate(mean_edges):
                total_mean_edges[i] += v

        if total_local_hypervolumes is None:
            total_local_hypervolumes = local_hypervolumes
        else:
            for i, v in enumerate(local_hypervolumes):
                total_local_hypervolumes[i] += v
        
    average_max_lengths = [x/run_count for x in total_max_lengths]
    average_mean_lengths = [x/run_count for x in total_mean_lengths]
    average_max_widths = [x/run_count for x in total_max_widths]
    average_mean_widths = [x/run_count for x in total_mean_widths]
    average_max_edges = [x/run_count for x in total_max_edges]
    average_mean_edges = [x/run_count for x in total_mean_edges]
    average_local_hypervolumes = [x/run_count for x in total_local_hypervolumes]
    return overall_best_hypervolume, overall_best_pareto_front, x_evals, average_max_lengths, average_mean_lengths, average_max_widths, average_mean_widths, average_max_edges, average_mean_edges, average_local_hypervolumes
