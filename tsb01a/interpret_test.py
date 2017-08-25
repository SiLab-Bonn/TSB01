from tsb01a.analysis import interpreter, calibration

calibration_path = '/media/tsb01a_data/debug/'
calibration_files = ['/media/tsb01a_data/debug/fe_new_chip1_pt00.h5',
                     '/media/tsb01a_data/debug/fe_new_chip1_pt01.h5',
                     '/media/tsb01a_data/debug/fe_new_chip1_pt02.h5',
                     '/media/tsb01a_data/debug/fe_new_chip1_pt03.h5',
                     '/media/tsb01a_data/debug/fe_new_chip1_pt04.h5',
                     '/media/tsb01a_data/debug/fe_new_chip1_pt05.h5',
                     '/media/tsb01a_data/debug/fe_new_chip1_pt06.h5',
                     '/media/tsb01a_data/debug/fe_new_chip1_pt07.h5',
                     '/media/tsb01a_data/debug/fe_new_chip1_pt08.h5',
                     '/media/tsb01a_data/debug/fe_new_chip1_pt09.h5']


interpreter = interpreter.Tsb01aInterpreter(calibration_files, 31, 12, 12)
# interpreter.interpret_data(output_file=calibration_path + 'interpreted.h5')

# interpreter.create_hit_table(input_file=calibration_path + 'interpreted.h5',
#                              output_file=calibration_path + 'Hits.h5',
#                              threshold=-100)

# plot_raw_data.mk_plot(path + 'bias_05_interpreted.h5', path + 'bias_05.pdf', 22, 9)
# hit_files = ['/media/tsb01a_data/calibration/700um/am241/Hits_pt00-19.h5',
#              '/media/tsb01a_data/calibration/700um/am241/Hits_pt20-39.h5',
#              '/media/tsb01a_data/calibration/700um/am241/Hits_pt40-59.h5',
#              '/media/tsb01a_data/calibration/700um/am241/Hits_pt60-79.h5']

distances = calibration.get_distance_map(calibration_path + "Hits.h5")
