import tables as tb
import matplotlib.pyplot as plt
import numpy as np

input_hits_file = '/media/tsb01a_data/testbeam_data_apr17/700um/v_bias_40/Hits_altered.h5'

with tb.open_file(input_hits_file, 'r') as in_file:
#     with tb.open_file('/media/tsb01a_data/testbeam_data_apr17/700um/v_bias_40/Hits_altered.h5', 'w') as out_file:
#         data = in_file.root.Hits[:]
#         description = data.dtype
#         print data
#         data["column"] = data["column"] - 16
#  
#         hit_table = out_file.create_table(out_file.root,
#                                           name="Hits",
#                                           description=description,
#                                           title="Hit data",
#                                           filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
#  
#         hit_table.append(data)
#         hit_table.flush()

    data = in_file.root.Hits[:]
    selection = np.where(np.logical_and(data["column"] == 7, data["row"] == 5))
    charge = data[selection]["charge"]
#     hist, edges = np.histogram(charge, bins=np.arange(0 - 500, 100000 + 500, 1000))
    hist, edges = np.histogram(charge, bins=np.arange(-10 - 0.5, 100 + 0.5, 1))
 
print hist
print edges
#     plt.bar(edges[:-1] - 500, hist, width=1000, fill=False, edgecolor='C0')
plt.hist(charge, range=(-5.5, 100000.5), bins=105)

plt.show()

# x = np.arange(0, 100, 0.1)
#
# plt.plot(x, x * x, 'C1--')
# plt.show()
