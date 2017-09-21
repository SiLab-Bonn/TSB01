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
# interpreter.interpret_data(output_file=calibration_path + 'interpreted.h5')
#
# interpreter.create_hit_table(input_file=calibration_path + 'interpreted.h5',
#                              output_file=calibration_path + 'Hits.h5',
#                              threshold=-100)

distances = calibration.get_distance_map(calibration_path + "Hits.h5", distance_guess=7, show_plots=True)

calibration.create_calibration(['/media/tsb01a_data/x-ray-tube/cu/calibration_cu.h5',
                                '/media/tsb01a_data/x-ray-tube/Niob/calibration_nb.h5',
                                '/media/tsb01a_data/x-ray-tube/test_with_fe_source/calibration_fe.h5'],
                               energies=[8040, 16615, 5899],
                               output_file='/media/tsb01a_data/x-ray-tube/calibration_test.h5',
                               show_plots=True)

# interpreter.create_hit_table(input_file=calibration_path + 'interpreted.h5',
#                              output_file=calibration_path + 'Hits_calibrated.h5',
#                              start_col=17,
#                              threshold=-100,
# #                            calibrate=False)
#                              calibrate=True,
#                              calibration_file='/media/tsb01a_data/x-ray-tube/calibration.h5')
