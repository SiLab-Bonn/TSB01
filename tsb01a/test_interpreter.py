import os

from tsb01a.analysis import interpreter, calibration

# use all h5 files from given folder that are not interpreted yet
path = '/media/tsb01a_data/testbeam_data_apr17/700um/v_bias_05/'
input_files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.h5') and 'pt' in file]


calibration_path = '/media/tsb01a_data/calibration/100um/fe55/'
calibration_files = [os.path.join(calibration_path, file) for file in os.listdir(calibration_path) if file.endswith('.h5') and 'pt' in file]

interpreter = interpreter.Tsb01aInterpreter(calibration_files, 31, 12, 12)
# interpreter.interpret_data()

# interpreter.create_hit_table(input_file=calibration_path + 'fe_calibration_interpreted.h5',
#                              output_file=calibration_path + 'Hits.h5',
#                              threshold=-50)

# plot_raw_data.mk_plot(path + 'bias_05_interpreted.h5', path + 'bias_05.pdf', 22, 9)
charge = calibration.get_pixel_data(calibration_path + "Hits.h5", col=23, row=11)
calibration.fit_spectrum(charge, peak_guess=8)