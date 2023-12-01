import matplotlib.pyplot as plt
def plot_versus_evals(mean_length, max_length, mean_width, max_width, hypervolume, evals, title):
    fig, ax = plt.subplots()
    ax.set(xlabel = 'Evaluations', title = title)
    ax2 = ax.twinx()

    ax.plot(evals, mean_length, 'g--')
    ax.plot(evals, max_length, 'g-')
    ax.plot(evals, mean_width, 'b--')
    ax.plot(evals, max_width, 'b-')
    ax.set(ylabel = 'Score')
    ax.legend(['Mean Length Score', 'Max Length Score', 'Mean Width Score', 'Max Width Score'],\
              loc = 'upper left', bbox_to_anchor = (0, -0.1))

    ax2.plot(evals, hypervolume, 'r:')
    ax2.set(ylabel = 'Hypervolume in objective score space')
    ax2.legend(['Hypervolume dominated by local Pareto front'],\
               loc = 'upper left', bbox_to_anchor = (0.8, -0.1))
    plt.show()

def plot_versus_evals_yellow(mean_length, max_length, mean_width, max_width, mean_edges, max_edges, hypervolume, evals, title):
    fig, ax = plt.subplots()
    ax.set(xlabel = 'Evaluations', title = title)
    ax2 = ax.twinx()

    ax.plot(evals, mean_length, 'g--')
    ax.plot(evals, max_length, 'g-')
    ax.plot(evals, mean_width, 'b--')
    ax.plot(evals, max_width, 'b-')
    ax.plot(evals, mean_edges, 'y--')
    ax.plot(evals, max_edges, 'y-')
    ax.set(ylabel = 'Score')
    ax.legend(['Mean Length Score', 'Max Length Score', 'Mean Width Score', 'Max Width Score', 'Mean Edges Score', 'Max Edges Score'],\
              loc = 'upper left', bbox_to_anchor = (0, -0.1))

    ax2.plot(evals, hypervolume, 'r:')
    ax2.set(ylabel = 'Hypervolume in objective score space')
    ax2.legend(['Hypervolume dominated by local Pareto front'],\
               loc = 'upper left', bbox_to_anchor = (0.8, -0.1))
    plt.show()


def plot_pareto_front(pareto_scores, title):
    # Matplotlib's stairs function has some unwanted behavior, so we do this manually.
    # It's a bit gross, but that's how custom matplotlib stuff often ends up...
    pareto_scores = sorted(pareto_scores, key=lambda score:score[0])
    pareto_y = []
    y_index = 0
    max_length = max(score[0] for score in pareto_scores)
    max_width = max(score[1] for score in pareto_scores)
    for x in range(max_length + 1):
        while x > pareto_scores[y_index][0]:
            y_index += 1
        pareto_y.append(pareto_scores[y_index][1])
    pareto_y.append(-2)

    fig, ax = plt.subplots()
    ax.set(xlabel = 'Length score', ylabel = 'Width score', title=title,
           xlim = [-1, max_length + 1], ylim = [-1, max_width + 1])
    ax.plot(pareto_y, drawstyle='steps-pre')
    ax.axhline(pareto_y[0], -1, 1/(max_length + 2))

    plt.show()