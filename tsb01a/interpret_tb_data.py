from tsb01a.analysis import interpreter

calibration_path = '/media/tsb01a_data/testbeam_data_apr17/700um/v_bias_40/'
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
# 
# interpreter.create_hit_table(input_file=calibration_path + 'bias_40_interpreted.h5',
#                              output_file=calibration_path + 'Hits.h5',
#                              threshold=0)

interpreter.create_hit_table(input_file=calibration_path + 'bias_40_interpreted.h5',
                             output_file=calibration_path + 'Hits_calibrated.h5',
                             start_col=17,
                             threshold=20,
                             calibrate=True,
                             calibration_file='/media/tsb01a_data/x-ray-tube/calibration.h5')
