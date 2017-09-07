""" Example how to create a charge histogram
"""

import tables as tb
import matplotlib.pyplot as plt

from tsb01a.analysis import interpreter, calibration

calibration_path = '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/'
calibration_files = ['/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt00.h5']
max_charge = 256
threshold = 0

# Create hit table from raw data
interpreter = interpreter.Tsb01aInterpreter(calibration_files, 31, 12, 12)
interpreter.interpret_data(output_file=calibration_path + 'interpreted.h5')
interpreter.create_hit_table(input_file=calibration_path + 'interpreted.h5',
                            output_file=calibration_path + 'Hits.h5',
                            threshold=threshold)
 

# Histogram the hits ibnto a 3D histogram *col, row, charge)
calibration.histogram_hits(hit_file=calibration_path + 'Hits.h5',
                           output_file=calibration_path + 'Hists.h5',
                           n_pixel_x=31,
                           n_pixel_y=12,
                           max_charge=max_charge,
                           min_charge=threshold)

# Plot the occupancy
with tb.open_file(calibration_path + 'Hists.h5') as in_file:
    hits_hists = in_file.root.HistHits[:]
    fig, ax = plt.subplots()
    # ax.bar(range(max_charge), hits_hists[10, 5])
    ax.bar(range(threshold, max_charge), hits_hists.sum(axis=(0, 1)))
    ax.set_title('One pixel charge histogram')
    plt.show()

    