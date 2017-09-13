""" Example how to create a charge histogram
"""

import numpy as np
import tables as tb
import matplotlib.pyplot as plt

from tsb01a.analysis import interpreter, calibration


def get_mean_from_histogram(counts, bin_positions, axis=0):
    return np.average(counts, axis=axis, weights=bin_positions) * bin_positions.sum() / np.nansum(counts, axis=axis)

def get_median_from_histogram(counts, bin_positions):
    return np.median(np.repeat(bin_positions, counts))

def get_rms_from_histogram(counts, bin_positions):   
    return np.std(np.repeat(bin_positions, counts))

calibration_path = '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/'
calibration_files = ['/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt00.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt01.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt02.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt03.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt04.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt05.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt06.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt07.h5',                    
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt08.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt09.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt10.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt11.h5',                    
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt12.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt13.h5',                    
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt14.h5']            
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
    bin_positions = range(threshold, max_charge)
    counts = hits_hists[:]
#     counts = hits_hists[10, 1]
    fig, ax = plt.subplots()
    ax.bar(range(threshold, max_charge), hits_hists.sum(axis=(0, 1)))
    sel = np.where(np.logical_and(bin_positions > 20,
                                 bin_positions < 100)) 
    get_mean_from_histogram(counts=counts[:, :, sel],
                            bin_positions=bin_positions[:, :, sel],
                            axis=2)                      
    ax.set_title('One pixel charge histogram')
    plt.show()

    