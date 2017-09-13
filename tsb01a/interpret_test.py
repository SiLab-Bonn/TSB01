import numpy as np
from tsb01a.analysis import interpreter, calibration
calibration_path = '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/'
calibration_files = ['/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt00.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt01.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt02.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt03.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt04.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt05.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt06.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt07.h5',                    
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt08.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt09.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt10.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt11.h5',                    
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt12.h5',
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt13.h5',                    
                     '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/cu/cu_target_pt14.h5'] #,
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/tsb_cu_data/fe_new_chip1_pt01.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/tsb_cu_data/fe_new_chip1_pt02.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/tsb_cu_data/fe_new_chip1_pt03.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/tsb_cu_data/fe_new_chip1_pt04.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/tsb_cu_data/fe_new_chip1_pt05.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/tsb_cu_data/fe_new_chip1_pt06.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/tsb_cu_data/fe_new_chip1_pt07.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/tsb_cu_data/fe_new_chip1_pt08.h5',
#                      '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/tsb_cu_data/fe_new_chip1_pt09.h5']

# interpreter = interpreter.Tsb01aInterpreter(calibration_files, 31, 12, 12)
# interpreter.interpret_data(output_file=calibration_path + 'interpreted.h5')
# 
# interpreter.create_hit_table(input_file=calibration_path + 'interpreted.h5',
#                             output_file=calibration_path + 'Hits.h5',
#                             threshold=-100)

#plot_raw_data.mk_plot(path + 'bias_05_interpreted.h5', path + 'bias_05.pdf', 22, 9)
# hit_files = ['/media/tsb01a_data/calibration/700um/am241/Hits_pt00-19.h5',
#              '/media/tsb01a_data/calibration/700um/am241/Hits_pt20-39.h5',
#              '/media/tsb01a_data/calibration/700um/am241/Hits_pt40-59.h5',
#              '/media/tsb01a_data/calibration/700um/am241/Hits_pt60-79.h5']

distances = calibration.get_distance_map(calibration_path + "Hits.h5")
import matplotlib.pyplot as plt
from matplotlib import cm
fig, ax = plt.subplots()
im = ax.imshow(distances, interpolation='nearest', aspect='auto')
ax.set_title('Difference between signal and Noise')
cbar = fig.colorbar(im)    # scale of vertical bar
plt.show()

  
import matplotlib.pyplot as plt
import tables as tb
import numpy as np
with tb.open_file(calibration_path + 'Hits.h5', "r") as in_file:
    hits = in_file.root.Hits[:]
    charge = hits[np.where(np.logical_and(hits["column"] == 11, hits["row"] == 6))]["charge"]
    hist, edges = np.histogram(charge, bins=np.arange(-25, 150, 1))
    plt.bar(edges[:-1], hist, width=1, fill=False, edgecolor='C0')
    plt.show()   
    
    