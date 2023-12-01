
# cutting_stock/visualizer.py

import cutting_stock.implementation as impl
import matplotlib.pyplot as plt

'''Creates a matplotlib figure visualizing a solution.

You shouldn't be calling this directly; it is wrapped in a function object returned by the fitness functions.

@param cells: dict of cells as output by a fitness function
@param shapes: shapes that were input to the fitness function
@param bounds: bounds that were input to the fitness function
@param visible_margin: width of out-of-bounds cells to display
@param path: path to save figure into; figure is instead shown to console if this evaluates to False
'''
def get_figure(cells, shapes, bounds, visible_margin, path = None, **kwargs):
    x_display = (bounds[0][0] - visible_margin, bounds[0][1] + visible_margin)
    y_display = (bounds[1][0] - visible_margin, bounds[1][1] + visible_margin)

    red = [None] * len(shapes)
    green = [None] * len(shapes)
    blue = [None] * len(shapes)
    for i in range(len(shapes)):
        red[i] = (5 * (i + 1) / len(shapes)) % 1.0
        green[i] = (3 * (i + 1) / len(shapes)) % 1.0
        blue[i] = (2 * (i + 1) / len(shapes)) % 1.0
    halfway = len(shapes) // 2
    red = red[:halfway] + list(reversed(red[halfway:]))
    green = list(reversed(green))

    # imshow axes are a bit backwards; y-axis comes first, x-axis second
    # Except for text... that's the normal order... and must be done after coloring, I think
    fig, ax = plt.subplots()
    rgbs = [[[1.0, 1.0, 1.0] for _ in range(*x_display)] for __ in range(*y_display)]
    overlaps = set()
    for cell, shapelist in cells.items():
        if impl.in_bounds(cell, (x_display, y_display)):
            if len(shapelist) > 1:
                rgbs[cell[1] + visible_margin][cell[0] + visible_margin] = [0.0, 0.0, 0.0]
                overlaps.add((cell[0] + visible_margin, cell[1] + visible_margin, len(shapelist)))
            else:
                rgbs[cell[1] + visible_margin][cell[0] + visible_margin] =\
                        [red[shapelist[0]],
                         green[shapelist[0]],
                         blue[shapelist[0]]]

    ax.imshow(rgbs, origin='lower')
    for overlap in overlaps:
        ax.text(overlap[0], overlap[1], str(overlap[2]),
                ha='center', va='center', fontsize='large', color='white')

    ax.grid(color='black', snap=True, linewidth=2)
    ax.set_xticks([bounds[0][0] + visible_margin - 0.5, bounds[0][1] + visible_margin - 0.5], ['min x', 'max x'])
    ax.set_yticks([bounds[1][0] + visible_margin - 0.5, bounds[1][1] + visible_margin - 0.5], ['min y', 'max y'])
    ax.margins=(0.01)

    if path:
        fig.savefig(path, bbox_inches = 'tight')
    else:
        fig.show()

