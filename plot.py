import numpy
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from os.path import join

import stats
import utils


def bar_chart(
    data, labels, output, title="Bar Chart", xlabel="x", ylabel="y", xmul=1, ymul=1
):

    N = len(labels)

    means, stds, mins, maxs = numpy.transpose(
        numpy.vstack(tuple(stats.summary(d) for d in data))
    )

    x_offsets = numpy.arange(N)
    width = 0.22

    fig, ax = plt.subplots()
    min_rects = ax.bar(x_offsets, mins, width, color="b", label="min")
    mean_rects = ax.bar(
        x_offsets + width, means, width, color="r", yerr=stds, label="mean"
    )
    max_rects = ax.bar(x_offsets + (2 * width), maxs, width, color="y", label="max")

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x_offsets + (1.5 * width))
    #    ax.set_xticklabels(numpy.fromfunction(
    #        function=lambda i: str(xmul*keys[i]), shape=(N,)))
    ax.set_xticklabels(list(map(str, xmul * labels)))

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))

    plt.savefig(join(output, title.replace(" ", "_") + ".png"), dpi=500)


def box_plot(
    data, labels, output, title="Box Plot", xlabel="x", ylabel="y", xmul=1, ymul=1
):
    """Makes a box plot"""
    N = len(labels)
    x_offsets = numpy.arange(N)

    fig, ax = plt.subplots()

    ax.boxplot(list(ymul * data))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(list(map(lambda x: str(int(x)), xmul * labels)))

    plt.savefig(join(output, title.replace(" ", "_") + ".png"), dpi=500)
