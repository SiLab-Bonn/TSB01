import tables as tb
import numpy as np
from matplotlib import pyplot as plt

path = '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/'
input_file = path + "Hits_Cluster.h5"

with tb.open_file(input_file, "r") as in_file_h5:
    cluster = in_file_h5.root.Cluster[:]
    sel = np.logical_and(cluster['seed_row'] != 10,
                         cluster['seed_column'] != 25)
    cluster = cluster[sel]

plt.hist(cluster['charge'], range=(0, 500), bins=100)
plt.show()
