from tsb01a import tsb01
import numpy as np
import tables as tb
import time

# Configuration
clk_divide = 12
n_cols = 32
n_rows = 12
reset = 10
delay = 10
exp = 50
howmuch = 270000  # length of data to record (possible to record multiple frames at once)

n_frames = 10000  # total number of datasets to record
filename = 'example_path/base_filename'  # extension and numbering will be added dynamically based on chunk size
file_length = 5000  # split data into files with this number of datasets


def record_data():
    # Initialize device
    device = tsb01.tsb01(channels=['OUTA2'])  # choose OUTA2 for 20um pixels, OUTA1 for 40um pixels
    device.init()
    device.sel_all(divide=clk_divide, howmuch=howmuch, repeat=0, reset=reset, delay0=delay, exp=exp,
                   size=(n_cols, n_rows))
    time.sleep(.1)

    # Start data taking
    for file_number in range(n_frames / file_length):
        with tb.open_file(filename + '_pt' + str(file_number).zfill(2) + '.h5', 'w') as out_file:
            waveforms = out_file.create_earray(out_file.root, name='event_data', atom=tb.UInt32Atom(),
                                               shape=(0, howmuch / 2), title='The raw events from the ADC',
                                               filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False),
                                               expectedrows=file_length)
            for t in xrange(file_length):
                raw_data = device.get_adc()
                raw_data = raw_data.reshape((1, howmuch / 2))

                if np.any(raw_data == None):
                    device.stop_adc()
                    device.init_adc(howmuch=howmuch)
                    print device['OUTA1'].is_done(), device['OUTA2'].is_done()
                    continue

                if device['OUTA1'].get_count_lost() != 0 or device['OUTA2'].get_count_lost() != 0:
                    print t, device['OUTA1'].get_count_lost(), device['OUTA2'].get_count_lost()
                    device.stop_adc()
                    device.init_adc(howmuch=howmuch)
                    print device['OUTA1'].is_done(), device['OUTA2'].is_done()
                    continue
                else:
                    waveforms.append(raw_data)
                    waveforms.flush()

if __name__ == "__main__":
    record_data()