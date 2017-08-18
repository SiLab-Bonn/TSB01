from tsb01a.analysis import interpreter, calibration

calibration_path = '/media/tsb01a_data/calibration/700um/am241/'
calibration_files = ['/media/tsb01a_data/calibration/700um/am241/am_calibration_pt80.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt81.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt82.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt83.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt84.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt85.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt86.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt87.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt88.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt89.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt80.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt91.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt92.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt93.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt94.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt95.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt96.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt97.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt98.h5',
                     '/media/tsb01a_data/calibration/700um/am241/am_calibration_pt99.h5']

interpreter = interpreter.Tsb01aInterpreter(calibration_files, 31, 12, 12)
interpreter.interpret_data(output_file=calibration_path + 'interpreted_test.h5')
#
# interpreter.create_hit_table(input_file=calibration_path + 'interpreted_pt80-99.h5',
#                              output_file=calibration_path + 'Hits_pt80-99.h5',
#                              threshold=-50)

# plot_raw_data.mk_plot(path + 'bias_05_interpreted.h5', path + 'bias_05.pdf', 22, 9)
# hit_files = ['/media/tsb01a_data/calibration/100um/am241/Hits_pt00-19.h5',
#              '/media/tsb01a_data/calibration/100um/am241/Hits_pt20-39.h5',
#              '/media/tsb01a_data/calibration/100um/am241/Hits_pt40-59.h5',
#              '/media/tsb01a_data/calibration/100um/am241/Hits_pt60-79.h5']

charge_1 = calibration.get_pixel_data(calibration_path + "Hits_pt00-19.h5", col=23, row=11)["charge"]
charge_2 = calibration.get_pixel_data(calibration_path + "Hits_pt20-39.h5", col=23, row=11)["charge"]
charge_3 = calibration.get_pixel_data(calibration_path + "Hits_pt40-59.h5", col=23, row=11)["charge"]
charge_4 = calibration.get_pixel_data(calibration_path + "Hits_pt60-79.h5", col=23, row=11)["charge"]
charge_5 = calibration.get_pixel_data(calibration_path + "Hits_pt80-99.h5", col=23, row=11)["charge"]
# charge_6 = calibration.get_pixel_data(calibration_path + "Hits_pt100-119.h5", col=23, row=11)
# charge_7 = calibration.get_pixel_data(calibration_path + "Hits_pt120-139.h5", col=23, row=11)
# charge_8 = calibration.get_pixel_data(calibration_path + "Hits_pt140-159.h5", col=23, row=11)
# charge_9 = calibration.get_pixel_data(calibration_path + "Hits_pt160-179.h5", col=23, row=11)
# charge_10 = calibration.get_pixel_data(calibration_path + "Hits_pt180-199.h5", col=23, row=11)

import numpy as np
total_charge = np.append(charge_1, charge_2)
print len(total_charge)
total_charge = np.append(total_charge, charge_3)
print len(total_charge)
total_charge = np.append(total_charge, charge_4)
print len(total_charge)
total_charge = np.append(total_charge, charge_5)
print len(total_charge)
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

calibration.fit_spectrum(total_charge, show_plots=True)
