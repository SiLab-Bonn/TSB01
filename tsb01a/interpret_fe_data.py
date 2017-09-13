from tsb01a.analysis import interpreter, calibration

calibration_path = '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/'
calibration_files = ['/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt00.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt01.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt02.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt03.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt04.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt05.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt06.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt07.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt08.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/fe_new_chip1_pt09.h5']


interpreter = interpreter.Tsb01aInterpreter(calibration_files, 31, 12, 12)
interpreter.interpret_data(output_file=calibration_path + 'interpreted.h5')
    
interpreter.create_hit_table(input_file=calibration_path + 'interpreted.h5',
                             output_file=calibration_path + 'Hits.h5',
                             threshold=-100)

# plot_raw_data.mk_plot(path + 'bias_05_interpreted.h5', path + 'bias_05.pdf', 22, 9)
# hit_files = ['/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/calibration/700um/am241/Hits_pt00-19.h5',
#              '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/calibration/700um/am241/Hits_pt20-39.h5',
#              '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/calibration/700um/am241/Hits_pt40-59.h5',
#              '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/calibration/700um/am241/Hits_pt60-79.h5']

# distances = calibration.get_distance_map(calibration_path + "Hits.h5", distance_guess=8, show_plots=True)

# print distances

# calibration.create_calibration(['/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/calibration_cu_flavor_2.h5',
#                                 '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/Niob/calibration_nb.h5',
#                                 '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/test_with_fe_source/calibration_fe.h5'],
#                                [8040, 16615, 5899], show_plots=False)

import numpy as np
import tables as tb
import matplotlib.pyplot as plt
# calibration.apply_calibration(np.ones(shape=(12, 15)), '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/calibration.h5')
 
interpreter.create_hit_table(input_file=calibration_path + 'interpreted.h5',
                             output_file=calibration_path + 'Hits_calibrated.h5',
                             threshold=-100,
                             calibrate=True,
                             calibration_file='/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/calibration.h5')

with tb.open_file(calibration_path + 'Hits_calibrated.h5', 'r') as in_file:
    hits = in_file.root.Hits[:]

    selection = np.where(np.logical_and(hits["column"] == 1, hits["row"] == 2))
    print hits[selection]
    charge = hits["charge"][selection] / 1000.
    calibration.fit_spectrum(charge, distance_guess=5, show_plots=True)

#     print hits
