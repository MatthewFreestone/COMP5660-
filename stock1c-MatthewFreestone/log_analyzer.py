
# log_analyzer.py

from statistics import mean

def format_log(log):
    return ''.join([entry + '\n' for entry in log])

def universal_analysis(log, evals):
    entries = [entry.split(': ') for entry in log]
    values = dict()
    for entry in entries:
        key = entry[0]
        val = entry[1]
        if key not in values:
            values[key] = [val]
        else:
            values[key].append(val)

    mu = int(values['mu'][0])
    num_children = int(values['num_children'][0])
    evaluations = [int(val) for val in values['Evaluations']]
    if evaluations[0] != mu:
        print('Initial evaluation count is incorrect.')
    for i in range(1, len(evaluations)):
        delta = evaluations[i] - evaluations[i-1]
        if delta != num_children:
            print('A generation increased the evaluation count by an incorrect amount. ' +\
                  'This could be a false positive caused by updating the evaluation count after survival selection.')
            break

    if evaluations[-1] < evals or evaluations[-1] >= evals + num_children:
        print('Final evaluation count seems incorrect.')

    child_counts = [int(val) for val in values['Number of children']]
    num_generations = len(child_counts)
    if any([count != num_children for count in child_counts]):
        print('Number of children seems incorrect.')

    combined_pre_pop_sizes = [int(val) for val in values['Pre-survival population size']]
    expected = mu + num_children
    if any([size != expected for size in combined_pre_pop_sizes]):
        print('Population size before survival selection seems incorrect.')

    combined_post_pop_sizes = [int(val) for val in values['Post-survival population size']]
    if any([size != mu for size in combined_post_pop_sizes]):
        print('Population size after survival selection seems incorrect.')

    if num_generations == 1:
        print('You only have one generation of children!')
        return values # short circuit the remaining checks

    mutations = [int(val) for val in values['Number of mutations']]
    total_mutations = sum(mutations)
    expected_mutations = float(values['mutation rate'][0]) * sum(child_counts)
    if total_mutations < expected_mutations * 0.75 or total_mutations > expected_mutations * 1.25:
        print('Total number of mutations over the course of the run seem incorrect.')

    if num_generations > 1 and all([mutation == mutations[0] for mutation in mutations]):
        print('Every generation mutated the same number of children. ' +\
              'This *may* be a sign you are checking the mutation rate incorrectly.')
              
    return values

def analyze_base_log(log, evals):
    values = universal_analysis(log, evals)
    means = [float(val) for val in values['Local mean']]
    best_mean_so_far = means[0]
    for i in range(1, len(means)):
        if means[i] > best_mean_so_far:
            best_mean_so_far = means[i]
        elif means[i] / best_mean_so_far < 0.75:
            print('Mean population fitness dropped significantly over time at least once. ' +\
                  'This *may* indicate a bug (especially if using truncation), or poor configuration. '+\
                  'You may ignore this if you deliberately chose a very non-elitist configuration and can justify your choice.')
            break

def analyze_constraint_satisfaction_log(log, evals):
    values = universal_analysis(log, evals)
    mean_penalized = [float(val) for val in values['Local mean penalized fitness']]
    max_penalized = [float(val) for val in values['Local best penalized fitness']]
    mean_base = [float(val) for val in values['Local mean base fitness']]
    max_base = [float(val) for val in values['Local best base fitness']]

    if any([len(x) != len(max_base) for x in [mean_penalized, max_penalized, mean_base]]):
        print('Different amounts of data recorded for different fitness metrics.')

    best_mean_so_far = mean_penalized[0]
    for i in range(1, len(mean_penalized)):
        if mean_penalized[i] > best_mean_so_far:
            best_mean_so_far = mean_penalized[i]
        elif mean_penalized[i] / best_mean_so_far < 0.75:
            print('Mean population penalized fitness dropped significantly over time at least once. ' +\
                  'This *may* indicate a bug (especially if using truncation), or poor configuration. '+\
                  'You may ignore this if you deliberately chose a very non-elitist configuration and can justify your choice.')
            break
