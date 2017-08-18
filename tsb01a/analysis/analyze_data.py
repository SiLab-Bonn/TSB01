import tables as tb
import numpy as np
from matplotlib import pyplot as plt


def plot_calibrated_spectrum(amplitudes, show_plots=False):
    #     print len(single_amplitudes)
    #     plt.hist(single_amplitudes, bins=np.arange(np.floor(np.min(single_amplitudes)) - 0.5, np.ceil(np.max(single_amplitudes)) + 0.5, 1))
    #     plt.show()

    hist, edges = np.histogram(amplitudes, bins=np.arange(-100, 25400, 500))

#     hist, edges = np.histogram(single_amplitudes, bins=25)
    if show_plots:
        #         plt.title('Pixel col: %s row: %s' %(col, row))
        plt.bar(edges[:-1] + 250, hist, align='center', width=500, alpha=1)
#         plt.show()

#     print np.sum(hist)

    return hist, edges


input_file = '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/Hits_calibrated_Cluster.h5'

with tb.open_file(input_file, 'r') as in_file_h5:
    all_hits = in_file_h5.root.Cluster[:]


selected_hits = all_hits[np.logical_and(all_hits['seed_row'] == 8, all_hits['seed_column'] == 5)]

cluster_size_one_hits = selected_hits[selected_hits['n_hits'] == 1]
cluster_size_two_hits = selected_hits[selected_hits['n_hits'] == 2]


print len(cluster_size_one_hits), len(selected_hits)

# plot_calibrated_spectrum(selected_hits['charge'], show_plots=True)
# plot_calibrated_spectrum(cluster_size_two_hits['charge'], show_plots=True)
plot_calibrated_spectrum(cluster_size_one_hits['charge'], show_plots=True)

plt.show()
