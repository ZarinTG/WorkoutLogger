import numpy as np
import matplotlib.pyplot as plt

def draw_chart(x_axis_name, y_axis_name, title, x_labels, bar_names, bar_value_map):
    n_groups = len(x_labels)
    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    colors=['b','g']
    for row_index, bar in enumerate(bar_names):
        if row_index % 2 == 0:
            color = colors[0]
        else:
            color = colors[1]

        bar_index = index
        if row_index != 0:
            bar_index = index + bar_width

        rects = plt.bar(bar_index, bar_value_map.get(bar), bar_width,
                         alpha=opacity,
                         color=color,
                         label=bar)
        ax.bar(bar_index,
               # using the pre_score data
               bar_value_map.get(bar),
               # set the width
               width=bar_width,
               # with alpha 0.5
               alpha=opacity,
               # with color
               color=color)

    plt.xlabel(x_axis_name)
    plt.ylabel(y_axis_name)
    plt.title(title)
    plt.xticks(index + bar_width, x_labels)
    plt.legend()

    #plt.tight_layout()
    plt.show()

