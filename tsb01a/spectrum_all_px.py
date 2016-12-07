import tsb01
import time
import numpy as np
import tables as tb
import logging
import os.path
import progressbar
from matplotlib import pyplot as plt
from scipy.constants.constants import alpha

clk_divide = 12
n_data_points = 800000
n_framesets = 5

# data = device.get_adc()[1]
def record_data(n_framesets):
    device = tsb01.tsb01()
    device.init()
    device.sel_all(howmuch=n_data_points, divide=clk_divide)
    
    time.sleep(.1)
    
    with tb.open_file('waveform_all_px.h5', 'w') as out_file:
        logging.info('Starting measurement')
        waveforms = out_file.create_earray(out_file.root, name='event_data', atom=tb.UIntAtom(), shape=(0, n_data_points), title='The raw events from the ADC', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False), expectedrows=n_framesets)
    
        for num in range(n_framesets):
            data = np.empty(shape=(1, n_data_points))

            #start adc to wait for next ADC_SYNC signal
#             device.start_adc()
            data[0,:] = device.get_adc()[1]
        #             plt.plot(data[0,:])
        #             plt.show()
            waveforms.append(data)
            waveforms.flush()
#             time.sleep(.005)
            
def read_data(frameset):
    '''
    Returns one dataset containing a number of consecutive frame (depending on the datapoints and clock divide)
    '''
    
    with tb.open_file('waveform_all_px.h5', 'r') as in_file:
        logging.info('Reading data')
        return in_file.root.event_data[frameset]

def analysis(raw_data, show_plots=False):
    data = raw_data
    
    x = np.arange(len(data))
    # print len(data)
    if show_plots:
        plt.plot(x, data, '-')
        # plt.plot(x[::4], data[::4], 'o')
        plt.show()

    # Take (hardcoded) third and fourth frame for analysis
    # 10 is offset from the beginning
    # 113 is to overlap the waveforms correctly
    first_frame = data[clk_divide * (1 * 20640 + 1 * 1000 + 10): clk_divide * (2 * 20640 + 1 * 1000 + 10)]
    second_frame = data[clk_divide * (2 * 20640 + 2 * 1000 - 113 + 10): clk_divide * (3 * 20640 + 2 * 1000 - 113 + 10)]

    # Plot raw data forms
    if show_plots:
        plt.plot(first_frame, 'b.-')
        plt.plot(second_frame, 'r.-')
        plt.show()

    # one row equals 215 sequencer clocks
    first_frame = first_frame.reshape(96, clk_divide * 215)
    second_frame = second_frame.reshape(96, clk_divide * 215)

    if show_plots:
        for one_row in range(96):
            plt.plot(first_frame[one_row], 'b.', alpha=0.2)
            plt.plot(second_frame[one_row], 'r.', alpha=0.2)
        plt.show()

    # region of interest (three flavors)
    # 47 = 16 + 16 + 15 columns 
    first_frame = first_frame[:,1388:1388 + 2 * clk_divide * 47].reshape(-1)
    second_frame = second_frame[:,1388:1388 + 2 * clk_divide * 47].reshape(-1)
    
    if show_plots:
        plt.plot(first_frame, 'b.')
        plt.plot(second_frame, 'r.')
        plt.show()
    
    after_reset = first_frame.reshape(96, clk_divide * 2* 47)
    before_reset = second_frame.reshape(96, clk_divide * 2* 47)
    
    pedestal = np.empty([96, 47])
    signal = np.empty([96, 47])
    
    for i in range(96):
        one_row = after_reset[i,:]
        one_row = one_row.reshape(47, clk_divide * 2)
        one_row = np.mean(one_row[:,3:17], axis=1)
        pedestal[i] = one_row
    
    for i in range(96):
        one_row = before_reset[i,:]
        one_row = one_row.reshape(47, clk_divide * 2)
        one_row = np.mean(one_row[:,3:17], axis=1)
        signal[i] = one_row
        
    pixel_values = pedestal - signal
    fig = plt.figure()
    ax1 = fig.add_subplot(131)
    ax1.set_title('Signal')
    im = ax1.imshow(signal, cmap=plt.get_cmap('viridis'), interpolation='none')
    fig.colorbar(im, ax=ax1)
    
    ax2 = fig.add_subplot(132)
    im = ax2.imshow(pedestal, cmap=plt.get_cmap('viridis'), interpolation='none')
    ax2.set_title('Pedestal')
    fig.colorbar(im, ax=ax2)
    
    ax3 = fig.add_subplot(133)
    im = ax3.imshow(pixel_values, cmap=plt.get_cmap('viridis'), interpolation='none')
    ax3.set_title('Amplitude')
    fig.colorbar(im, ax=ax3)
    
    # number of negative entries
    print 'total negative signal', len(pixel_values.reshape(-1)[pixel_values.reshape(-1) < 0])
    print 'negative signal in last flavor', len(pixel_values[:, 32:].reshape(-1)[pixel_values[:, 32:].reshape(-1) < 0])
    
    plt.show()

start = time.clock()
record_data(n_framesets=5)
stop = time.clock()
  
print stop - start

for frameset in range(5):
    data = read_data(frameset)
    analysis(data)
