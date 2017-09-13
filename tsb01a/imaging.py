import tsb01
import numpy as np
from matplotlib import pyplot as plt
import tables as tb
import time
import logging
from scipy.optimize import curve_fit

clk_divide = 12
n_cols = 32
n_rows = 12
reset = 10
delay = 10
exp = 50
howmuch = 270000


n_frames = 15000
filename = '/media/silab/9c56be36-6e1d-4765-9417-09384db0babf/x-ray-tube/BKG_200_40/BKG'
file_length = 1000

def record_data():

    # Initialize device
    device = tsb01.tsb01(channels=['OUTA2'])
    device.init()
    device.sel_all(divide=clk_divide, howmuch=howmuch, repeat=0, reset=reset, delay0=delay, exp=exp, size=(n_cols, n_rows))
    time.sleep(.1)
    
    # Start data taking
    for file_number in range(n_frames / file_length):
        with tb.open_file(filename+'_pt'+str(file_number).zfill(2)+'.h5', 'w') as out_file:
            waveforms = out_file.create_earray(out_file.root, name='event_data', atom=tb.UInt32Atom(), shape=(0, howmuch / 2), title='The raw events from the ADC', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False), expectedrows=file_length)
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
                #             plt.plot(raw_data[0,:])
                #             plt.show()
                    waveforms.append(raw_data)
                    waveforms.flush()


def analyze_nmdata(nmdata):
    single = False

    val1 = np.bitwise_and(nmdata, 0x00003fff)
    vals = np.right_shift(np.bitwise_and(nmdata, 0x10000000), 28)
    valc = np.right_shift(np.bitwise_and(nmdata, 0x60000000), 29)

    if(not single):
        val0 = np.right_shift(np.bitwise_and(nmdata, 0x0fffc000), 14)
        val1 = np.reshape(np.vstack((val0, val1)), -1, order='F')
#         unused variable sync
#         sync = np.reshape(np.vstack((vals, vals)), -1, order='F')
        valc = np.reshape(np.vstack((valc, valc)), -1, order='F')
    val = np.empty([2, len(val1) / 2], dtype=np.int32)
    for i in [0, 1]:
        val0 = val1[valc == i]
        if len(val[i, :]) == len(val0):
            val[i, :] = val1[valc == i]
        elif len(val[i, :]) < len(val0):
            val[i, :] = val1[valc == i][:len(val[i, :])]
            # print "WARN data size: all=",len(val1),"ch%d"%i,len(val[i,:]),"dat=",len(val0)
        else:
            val[i, :len(val0)] = val1[valc == i]
            val[i, len(val0):] = 0
            # print "WARN data size: all=",len(val1),"ch%d"%i,len(val[i,:]),"dat=",len(val0)
    return val


# @profile
def get_signal(data, show_plots=False):
    frame_length = n_rows * (2 * n_cols + 1 + reset + delay + 2 * n_cols + 2) # + 1 + exp + 3
    
    # Determine offset manually to make sure frames are 100% overlapping
    offset = 0
    
    # from start point, go through all the columns, then change for next row and go through all columns again
    # in 96 rows, 95 row changes are performed, therefore (n_rows - 1)
    first_frame = data[54:54 + clk_divide * frame_length]
    second_frame = data[offset + 54 + clk_divide * frame_length + clk_divide * (1 + exp + 3):offset + 54 + 2 * clk_divide * frame_length + clk_divide * (1 + exp + 3)]
#     plt.plot(data, 'ro-')
# 
#     x = np.arange(0, len(first_frame))
#     plt.plot(first_frame, 'b.-')
#     plt.plot(x, second_frame, 'r.-')
#     plt.show()
    
    # trim to pixels after reset
    first_frame = first_frame.reshape((n_rows, clk_divide * (2 * n_cols + 1 + reset + delay + 2 * n_cols + 2)))
    
#     plt.plot(first_frame[0])

    
    first_frame = first_frame[:,2 * clk_divide * n_cols + clk_divide + reset * clk_divide + delay * clk_divide:- 2 * clk_divide]
    
#     print len(first_frame[0])
#     plt.plot(first_frame[0])

    
    # trim to pixels before reset
    second_frame = second_frame.reshape((n_rows, clk_divide * (2 * n_cols + 1 + reset + delay + 2 * n_cols + 2)))
    
#     plt.plot(second_frame[<10])
    
    second_frame = second_frame[:,:2 * clk_divide * n_cols]

#     plt.plot(second_frame[10])

#     plt.show()

#     fig = plt.figure()
#     
#     ax = fig.add_subplot(211)
#     im = ax.imshow(first_frame, cmap=plt.get_cmap('viridis'), aspect='auto', interpolation='none', vmin=np.amin(second_frame), vmax=np.amax(first_frame))
#     fig.colorbar(im, ax=ax)
#     
#         
#     ax = fig.add_subplot(212)
#     im = ax.imshow(second_frame, cmap=plt.get_cmap('viridis'), aspect='auto', interpolation='none', vmin=np.amin(second_frame), vmax=np.amax(first_frame))
#     fig.colorbar(im, ax=ax)
#         
#     plt.show()

    # Make array with values from one pixel in one row
    # Then generate single value for every pixel using median (more robust against outliers than mean)
    # Afterwards reshape array to correspond to pixel matrix
    first_frame = first_frame.reshape((n_cols * n_rows, 2 * clk_divide))
    first_frame = np.median(first_frame, axis=1)
    first_frame = first_frame.reshape((n_rows, n_cols))

    second_frame = second_frame.reshape((n_cols * n_rows, 2 * clk_divide))
    second_frame = np.median(second_frame, axis=1)
    second_frame = second_frame.reshape((n_rows, n_cols))

#     fig = plt.figure()
#     ax1 = fig.add_subplot(131)
#     ax1.set_title("After reset")
#     im = ax1.imshow(first_frame / 10., cmap=plt.get_cmap('viridis'), interpolation='none', vmin=np.amin(second_frame / 10.), vmax=np.amax(first_frame / 10.))
#     fig.colorbar(im, ax=ax1)
#         
#     ax2 = fig.add_subplot(132)
#     ax2.set_title("Before reset")
#     im = ax2.imshow(second_frame / 10., cmap=plt.get_cmap('viridis'), interpolation='none', vmin=np.amin(second_frame / 10.), vmax=np.amax(first_frame / 10.))
#     fig.colorbar(im, ax=ax2)

#     plt.show()
    
    signal = first_frame - second_frame
    
    if show_plots:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Signal (after reset - before reset)')
        im = ax.imshow(signal, interpolation='none')
        fig.colorbar(im, ax=ax)
        plt.show()

    return signal


# @profile
def read_data(filename, chunk_size):
    """
    Read data from file in chunks
    Return first chunk_size datasets
    Use chunk_size = None for all datasets
    """
    

    with tb.open_file(filename, 'r') as in_file:
        nmdata = in_file.root.event_data[:chunk_size]
    return nmdata


def plot_single_spectrum(amplitudes, row, col, show_plots=False):
    single_amplitudes = amplitudes[:,row,col]
    print len(single_amplitudes)
#     plt.hist(single_amplitudes, bins=np.arange(np.floor(np.min(single_amplitudes)) - 0.5, np.ceil(np.max(single_amplitudes)) + 0.5, 1))
#     plt.show()
    
    hist, edges = np.histogram(single_amplitudes, bins=np.arange(np.floor(np.min(single_amplitudes)) - 0.5, np.ceil(np.max(single_amplitudes)) + 0.5, 1))
    if show_plots:
        plt.title('Pixel col: %s row: %s' %(col, row))
        plt.bar(edges[:-1] + .5, hist, align='center', width=1)
#         plt.ylabel('Counts')
#         plt.xlabel('ADC units')
#         plt.yscale('log')
        plt.show()
    
#     print np.sum(hist)
    
    return hist, edges


def calculate_amplitudes(filenames):
    logging.info('Start analysis')
    
    # prepare array to hold analyzed data in form of stacked 2d images
    amplitudes = np.empty(shape=(n_rows, n_cols))
    amplitudes = amplitudes[np.newaxis,:,:]
    
    pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='#', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=len(filenames), poll=10, term_width=80).start()
    
    for index, filename in enumerate(filenames):
        data_from_file = read_data(filename, 10000)
    
        for raw_data in data_from_file:
            data = analyze_nmdata(raw_data)[1]
            amplitudes = np.append(amplitudes, get_signal(data)[np.newaxis,:,:], axis=0)
        
        pbar.update(index)
    
    pbar.finish()
      
    logging.info('End analysis')
    

    # truncate first image which is from np.empty initialization and return
    return amplitudes[1:,:,:]


# TODO: Exception fangen wenn Fit nicht konvergiert
def fit_spectrum_gauss(amplitudes):
    
    hist, edges = np.histogram(amplitudes, bins=np.arange(-50 - 0.5, 50 + 0.5, .5))
    
    mids = (edges + 0.25)


    def gauss(x, mean, sigma, amp):
        return amp * np.exp( - (x - mean)*(x - mean) / (2 * sigma * sigma))

#     print hist[np.where(hist == np.amax(hist))[0]]

#     if show_plots:
#         plt.bar(mids[:-1], hist, align='center', width=.5)
#         plt.show()

    
    ped_index = np.where(hist == np.amax(hist))[0][0]
    ped_mean = mids[np.where(hist == np.amax(hist))[0][0]]
    peak_index = np.where(np.diff(hist) > 5)[0][-1]
    peak_mean = mids[np.where(np.diff(hist) > 5)[0][-1]]

#     print peak_mean

#     plt.bar(mids[:-1], hist, align='center', width=.5)
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), ped_mean, .5, np.amax(hist)) + gauss(np.arange(mids[0], mids[-1], 0.1), peak_mean, .5, 0.027 * np.amax(hist)), "r-", linewidth=2, label='initial guess')
#     plt.xlim(-5, 20)

    try:
        ped_coeff, _ = curve_fit(gauss, mids[ped_index - 10:ped_index + 10], hist[ped_index - 10:ped_index + 10], p0=(ped_mean, 2., np.amax(hist)), sigma=10, absolute_sigma=True)
    
#         plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *ped_coeff) + gauss(np.arange(mids[0], mids[-1], 0.1), peak_mean, .5, 0.027 * np.amax(hist)), "m-", linewidth=2, label='between fits')

        lower_bound = np.argwhere(mids > ped_coeff[0] + 4 * ped_coeff[1])[0][0]
#         print mids[lower_bound:peak_index + 20]
        
        test = np.amax([lower_bound, peak_index -10])

#         print mids[test]
        peak_coeff, _ = curve_fit(gauss, mids[test:peak_index + 20], hist[test:peak_index + 20], p0=(peak_mean, 1, 0.027 * np.amax(hist)), sigma=1, absolute_sigma=True)
    
    # TODO: better error handling
    except RuntimeError:
        print 'Error occured'
        plt.legend(loc=0)
#         plt.show()
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}
    except ValueError:
        print 'Error occured'
        plt.legend(loc=0)
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

#         plt.show()
 
#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}
    except TypeError:
        print 'Error occured'
        plt.legend(loc=0)
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

#         plt.show()
 
#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}


#     plt.ylim(0, 3000)
#     plt.xlabel('ADC units')
#     plt.ylabel('Counts')
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *ped_coeff), "g-", linewidth=2, label='result')
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *peak_coeff), "g-", linewidth=2)
#     plt.legend(loc=0)
# 
#     plt.show()

    pedestal = {'mean': ped_coeff[0], 'sigma': np.abs(ped_coeff[1]), 'amp': ped_coeff[2]}
    peak = {'mean': peak_coeff[0], 'sigma': np.abs(peak_coeff[1]), 'amp': peak_coeff[2]}
    
    return pedestal, peak


def fit_spectrum_langau(amplitudes):

    hist, edges = np.histogram(amplitudes, bins=np.arange(-50 - 0.5, 140 + 0.5, 1))

    mids = (edges + 0.5)


    def gauss(x, mean, sigma, amp):
        return amp * np.exp( - (x - mean)*(x - mean) / (2 * sigma * sigma))

#     print hist[np.where(hist == np.amax(hist))[0]]

#     plt.bar(mids[:-1], hist, align='center', width=1)
#     plt.show()

    
    ped_index = np.where(hist == np.amax(hist))[0][0]
    ped_mean = mids[np.where(hist == np.amax(hist))[0][0]]
#     peak_index = np.where(np.diff(hist) > 10000)[0][-1]
    peak_index = 110
    peak_mean = 60
#     peak_mean = mids[np.where(np.diff(hist) > 5000)[0][-1]]


#     print peak_mean

#     plt.bar(mids[:-1], hist, align='center', width=1)
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), ped_mean, 2., np.amax(hist)) + gauss(np.arange(mids[0], mids[-1], 0.1), peak_mean, 10., 0.004 * np.amax(hist)), "r-", linewidth=2, label='initial guess')
#     plt.xlim(-5, 120)
#     plt.ylim(None, 80000)
#     plt.show()


    try:
        ped_coeff, _ = curve_fit(gauss, mids[ped_index - 10:ped_index + 10], hist[ped_index - 10:ped_index + 10], p0=(ped_mean, 2, np.amax(hist)), sigma=None, absolute_sigma=True)
    
#         plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *ped_coeff) + gauss(np.arange(mids[0], mids[-1], 0.1), peak_mean, .5, 0.027 * np.amax(hist)), "m-", linewidth=2, label='between fits')

        lower_bound = np.argwhere(mids > ped_coeff[0] + 4 * ped_coeff[1])[0][0]
#         print mids[lower_bound:peak_index + 20]
        
        test = np.amax([lower_bound, peak_index -10])

#         print mids[test]
        peak_coeff, _ = curve_fit(gauss, mids[test:peak_index + 20], hist[test:peak_index + 20], p0=(peak_mean, 5, 0.005 * np.amax(hist)), sigma=None, absolute_sigma=True)
    
    # TODO: better error handling
    except RuntimeError:
        print 'RuntimeError occured'
#         plt.legend(loc=0)
#         plt.show()
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}
    except ValueError:
        print 'ValueError occured'
        plt.legend(loc=0)
        plt.show()
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}
 
#         plt.show()
 
#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}
    except TypeError:
        print 'TypeError occured'
        plt.legend(loc=0)
        plt.show()
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

#         plt.show()
 
#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}


#     plt.ylim(0, 3000)
#     plt.xlabel('ADC units')
#     plt.ylabel('Counts')
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *ped_coeff), "g-", linewidth=2, label='result')
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *peak_coeff), "g-", linewidth=2)
#     plt.legend(loc=0)
#
#     plt.show()

    pedestal = {'mean': ped_coeff[0], 'sigma': np.abs(ped_coeff[1]), 'amp': ped_coeff[2]}
    peak = {'mean': peak_coeff[0], 'sigma': np.abs(peak_coeff[1]), 'amp': peak_coeff[2]}
    
    return pedestal, peak



def create_hit_table(hits):
    event_numbers = np.arange(0, len(amplitudes), 1)

    hit_indices = np.argwhere(hits != 0)

    col, row, charge = np.zeros((len(hit_indices))), np.zeros((len(hit_indices))), np.zeros((len(hit_indices)))
    frame_numbers = np.zeros((len(hit_indices)))
    event_numbers = np.zeros((len(hit_indices)))

    for index, hit in enumerate(hit_indices):
        try:
            event_numbers[index], col[index], row[index], charge[index] = hit[0] + 1, hit[2] + 1, hit[1] + 1, hits[hit[0], hit[1], hit[2]]
        except IndexError:
            print index, hit
            
    array = np.stack((event_numbers, frame_numbers, col, row, charge), axis=-1)
    

    hit_table = np.core.records.fromarrays(array.transpose(), 
                                             names='event_number, frame, column, row, charge',
                                             formats = '<i4, <u1, <u2, <u2, <u4')

    del array

    with tb.open_file('/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/Hits.h5', 'w') as out_file:
#         hit_table = out_file.create_table(where=out_file.root, title='Hit information', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False), expectedrows=len(hit_table), obj=hit_table)
#         hit_table = out_file.create_table(where=out_file.root, obj=hit_table)
        hits = out_file.create_table(out_file.root,
                                      name='Hits',
                                      title='Amplitudes larger than baseline',
                                      description=hit_table.dtype,
                                      filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
        hits.append(hit_table)

    return


def get_hits(amplitudes):
    """
    Iterate over all pixels to determine threshold for hit and calculate number of hits in this pixel
    """

    # Prepare hits array to be filled and to generate indices  
    hit_map = np.zeros((amplitudes.shape[1], amplitudes.shape[2]))

    # Create array with event numbers
    hits = np.zeros((amplitudes.shape[1], amplitudes.shape[2], len(amplitudes)))

    for index, _ in np.ndenumerate(hit_map):
#         hist, edges = plot_single_spectrum(amplitudes, index[0], index[1])
        pedestal, peak = fit_spectrum_langau(amplitudes[:,index[0], index[1]])
        one_pixel_amplitudes = amplitudes[:, index[0], index[1]] # - pedestal['mean']
        one_pixel_amplitudes[one_pixel_amplitudes < (peak['mean'] - 2 * peak['sigma'])] = 0

        # Create hit array where non-hits have been set to 0 and amplitude is preserved
        hits[index[0], index[1]] = one_pixel_amplitudes

        # Create hit array where number of hits are counted with setting all hits to 1
#         one_pixel_amplitudes[one_pixel_amplitudes >= pedestal['mean'] + 3 * pedestal['sigma']] = 1
        hit_map[index[0], index[1]] = np.sum(one_pixel_amplitudes, axis=0)

    hits = np.transpose(hits, axes=(2, 0, 1))

    return hit_map, hits


start_record = time.time()
record_data()
end_record = time.time()
print 'recording took: ', end_record - start_record

v_bias_40 = ['/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt00.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt01.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt02.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt03.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt04.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt05.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt06.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt07.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt08.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt09.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt10.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt11.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt12.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt13.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt14.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt15.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt16.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt17.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt18.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt19.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt20.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt21.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt22.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt23.h5',
             '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/250000_pt24.h5',
             ]

v_bias_30 = ['/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/testbeam_data_mar17/imaging/v_bias_30/100000_pt00.h5'
             ]


# tb_data = '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/testbeam_data_dec16/all_px/30000_pt05.h5'
# fe_data = ['/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt00.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt01.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt02.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt03.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt04.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt05.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt06.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt07.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt08.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_pt09.h5']
#
# cd_data = ['/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt00.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt01.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt02.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt03.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt04.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt05.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt06.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt07.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt08.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt09.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt10.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt11.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt12.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt13.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt14.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt15.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt16.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt17.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt18.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/47x12_100000_pt19.h5']
#
# am_data = ['/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/47x12_100000_pt00.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/47x12_100000_pt01.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/47x12_100000_pt02.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/47x12_100000_pt03.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/47x12_100000_pt04.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/47x12_100000_pt05.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/47x12_100000_pt06.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/47x12_100000_pt07.h5',
#            '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/47x12_100000_pt08.h5']

# amplitudes = calculate_amplitudes(filenames=v_bias_40)

# np.save('/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/amplitudes_raw.npy', amplitudes)

# amplitudes = np.load('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/am_source/amplitudes_47x12_100000.npy')
# amplitudes = np.load('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/cd_source/amplitudes_47x12_100000.npy')
# amplitudes = np.load('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/amplitudes_47x12_50000.npy')

# amplitudes = np.load('/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/amplitudes_raw.npy')
# 
# 
# hist, edges = plot_single_spectrum(amplitudes, row=10, col=22, show_plots=True)
# _, _ = fit_spectrum_langau(amplitudes)
# 
# 
# hit_map, hits = get_hits(amplitudes[:, :, 16:32])
# 
# # plot_single_spectrum(hits, row=10, col=31, show_plots=True)
# 
# # amplitudes = amplitudes.reshape((len(amplitudes), 96 * 47))
# 
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.set_title('Hits (binary)')
# im = ax.imshow(hit_map, interpolation='none')
# fig.colorbar(im, ax=ax)
# plt.show()
# 
# create_hit_table(hits)

# print 'analysis took: ', end_analysis - start_analysis
