from tsb01a.analysis import interpreter, calibration

calibration_path = '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/'
calibration_files = ['/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt00.h5',
                     '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt01.h5',
                     '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt02.h5',
                     '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt03.h5',
                     '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt04.h5',
                     '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt05.h5',
                     '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt06.h5',
                     '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt07.h5',
                     '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt08.h5',
                     '/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/bias_40_pt09.h5']

interpreter = interpreter.Tsb01aInterpreter(calibration_files, 31, 12, 12)
# interpreter.interpret_data(output_file=calibration_path + 'bias_40_interpreted.h5')

interpreter.create_hit_table(input_file=calibration_path + 'bias_40_interpreted.h5',
                             output_file=calibration_path + 'Hits.h5',
                             threshold=0)

# plot_raw_data.mk_plot(path + 'bias_05_interpreted.h5', path + 'bias_05.pdf', 22, 9)
# hit_files = ['/media/tsb01a_data/calibration/100um/am241/Hits_pt00-19.h5',
#              '/media/tsb01a_data/calibration/100um/am241/Hits_pt20-39.h5',
#              '/media/tsb01a_data/calibration/100um/am241/Hits_pt40-59.h5',
#              '/media/tsb01a_data/calibration/100um/am241/Hits_pt60-79.h5']

charge = calibration.get_pixel_data(calibration_path + "Hits.h5", col=12, row=11)["charge"]
# charge_6 = calibration.get_pixel_data(calibration_path + "Hits_pt100-119.h5", col=23, row=11)
# charge_7 = calibration.get_pixel_data(calibration_path + "Hits_pt120-139.h5", col=23, row=11)
# charge_8 = calibration.get_pixel_data(calibration_path + "Hits_pt140-159.h5", col=23, row=11)
# charge_9 = calibration.get_pixel_data(calibration_path + "Hits_pt160-179.h5", col=23, row=11)
# charge_10 = calibration.get_pixel_data(calibration_path + "Hits_pt180-199.h5", col=23, row=11)

import numpy as np

# total_charge = np.append(total_charge, charge_6)
# print len(total_charge)
# total_charge = np.append(total_charge, charge_7)
# print len(total_charge)
# total_charge = np.append(total_charge, charge_8)
# print len(total_charge)
# total_charge = np.append(total_charge, charge_9)
# print len(total_charge)
# total_charge = np.append(total_charge, charge_10)
# print len(total_charge)

calibration.fit_spectrum(charge, show_plots=True)
