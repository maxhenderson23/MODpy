import numpy as np
import matplotlib.pyplot as pl

list_of_colors = ['r', 'b', 'k']

def plot(name, title, list_of_data, list_of_labels, axis_labels, y_log = False):
    pl.figure(name)
    pl.title(title)

    hists = []
    for data in list_of_data:
        hists.append(np.histogram(data, bins=100, density=True))

    for i, hist in enumerate(hists):
        pl.plot((hist[1][:-1] + hist[1][1:])/2, hist[0], label=list_of_labels[i], color=list_of_colors[i])

    pl.xlabel(axis_labels[0])
    pl.ylabel(axis_labels[1])
    if y_log:
        pl.yscale('log')
    pl.legend(loc='best')
    pl.grid()

    pl.show()
