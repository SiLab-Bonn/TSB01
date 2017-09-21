import tsb01
import time
import numpy as np
import tables as tb
import logging
import os.path
import progressbar
from matplotlib import pyplot as plt

clk_divide = 12
n_data_points = 525000
n_framesets = 10000
file_length = 2500

# data = device.get_adc()[1]
def record_data(n_framesets, filename, overwrite=False):
    # Checks if file already exists if not stated otherwise
    if not overwrite and os.path.isfile(filename):
        logging.info('File already exists, abort.')
        return
    
# TODO: save configuration in data file
    device = tsb01.tsb01()
    device.init()
    device.sel_all(howmuch=n_data_points, divide=clk_divide, repeat=0)
    print device['OUTA1'].is_done(), device['OUTA2'].is_done()
    time.sleep(.1)

    logging.info('Starting measurement')
    pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='#', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=n_framesets, poll=10, term_width=80).start()
    for file_number in range(n_framesets / file_length):

        with tb.open_file(filename+'_pt'+str(file_number).zfill(2)+'.h5', 'w') as out_file:
            waveforms = out_file.create_earray(out_file.root, name='event_data', atom=tb.UInt32Atom(), shape=(0, n_data_points), title='The raw events from the ADC', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False), expectedrows=n_framesets)
    #         configuration = out_file.create_earray(out_file.root, name='settings', title='Settings for data taking')
    #         configuration.append(n_data_points)
    #         configuration.flush()
    
            for t in xrange(file_length):
                data = np.empty(shape=(1, n_data_points))
    
                raw_data = device.get_adc()
                
                if np.any(raw_data == None):
                    device.stop_adc()
                    device.init_adc(howmuch=n_data_points)
                    print device['OUTA1'].is_done(), device['OUTA2'].is_done()
                    continue
    
                if t % 20 == 0:
                    pbar.update(file_number * file_length + t)
    
                # Check for lost data          
                if device['OUTA1'].get_count_lost() != 0 or device['OUTA2'].get_count_lost() != 0:
                    print t, device['OUTA1'].get_count_lost(), device['OUTA2'].get_count_lost()
                    device.stop_adc()
                    device.init_adc(howmuch=n_data_points)
                    print device['OUTA1'].is_done(), device['OUTA2'].is_done()
                    continue
                else:
                    data[0,:] = raw_data
                #             plt.plot(data[0,:])
                #             plt.show()
                    waveforms.append(data)
                    waveforms.flush()
        #             time.sleep(.005)
    pbar.finish()


def hit_monitor(raw_data, threshold=20):
    # Fast analysis to print some hits
    first_frame = raw_data[clk_divide * (0 * 20640 + 0 * 1000 + 10): clk_divide * (1 * 20640 + 0 * 1000 + 10)]
    second_frame = raw_data[clk_divide * (1 * 20640 + 1 * 1000 - 113 + 10): clk_divide * (2 * 20640 + 1 * 1000 - 113 + 10)]

    # fold data of all rows into one
    first_frame = first_frame.reshape(96, clk_divide * 215)
    second_frame = second_frame.reshape(96, clk_divide * 215)

    # select region of signal
    first_frame = first_frame[:,1388:1388 + 2 * clk_divide * 47].reshape(-1)
    second_frame = second_frame[:,1388:1388 + 2 * clk_divide * 47].reshape(-1)

    after_reset = first_frame.reshape(96, clk_divide * 2* 47)
    before_reset = second_frame.reshape(96, clk_divide * 2* 47)

    pedestal = np.empty([96, 47])
    signal = np.empty([96, 47])

    for i in range(96):
        row_after_rst = after_reset[i,:]
        row_after_rst = row_after_rst.reshape(47, clk_divide * 2)
        row_after_rst = np.mean(row_after_rst[:,3:17], axis=1)
        pedestal[i] = row_after_rst
        
        row_before_rst = before_reset[i,:]
        row_before_rst = row_before_rst.reshape(47, clk_divide * 2)
        row_before_rst = np.mean(row_before_rst[:,3:17], axis=1)
        signal[i] = row_before_rst

    pixel_values = pedestal - signal
    
    pixel_values[pixel_values > threshold] = 1
    pixel_values[pixel_values <= threshold] = 0

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('Binary hits')
    im = ax.imshow(signal, cmap=plt.get_cmap('viridis'), interpolation='none')
    fig.colorbar(im, ax=ax)
    

# start = time.clock()
record_data(n_framesets=n_framesets, filename='/home/remote/Documents/iron_data/all_px/10000_without_source')
# stop = time.clock()
      
# print stop - start