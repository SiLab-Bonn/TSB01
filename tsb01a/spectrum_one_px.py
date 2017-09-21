from matplotlib import pyplot as plt
import numpy as np
import tables as tb
import time
import progressbar
import os.path
import logging

from scipy.signal import medfilt
from numba import jit, njit

from lmfit import Model
from lmfit.models import GaussianModel

from scipy.optimize import curve_fit

file_length = 10000


def analyze_nmdata(nmdata):
        single = False
        
        val1 = np.bitwise_and(nmdata, 0x00003fff)
        vals = np.right_shift(np.bitwise_and(nmdata, 0x10000000), 28)
        valc = np.right_shift(np.bitwise_and(nmdata, 0x60000000), 29)
       
        if(not single):
            val0 = np.right_shift(np.bitwise_and(nmdata, 0x0fffc000), 14)
            val1 = np.reshape(np.vstack((val0, val1)), -1, order='F')
            # unused variable sync
#             sync = np.reshape(np.vstack((vals, vals)), -1, order='F')
            valc = np.reshape(np.vstack((valc, valc)), -1, order='F')
        # return val1
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


def record_data(filename='waveform_data', n_samples=5000, overwrite=False):
    '''
    Take n_samples waveforms and save them to a pyTables file 
    '''

    # Checks if file already exists if not stated otherwise
    if not overwrite and os.path.isfile(filename):
        logging.info('File already exists, abort.')
        return
    
    import tsb01

    # initialize device
    device = tsb01.tsb01()
    device.init()
    device.sel_one(row=10, col=35, howmuch=100000)
    
    pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='#', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=n_samples, poll=10, term_width=80).start()

    logging.info('Starting measurement')

    for file_number in range(n_samples / file_length):

        with tb.open_file(filename+'_pt'+str(file_number).zfill(2)+'.h5', 'w') as out_file:
            waveforms = out_file.create_earray(out_file.root, name='event_data', atom=tb.UIntAtom(), shape=(0,100000), title='The raw events from the ADC', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False), expectedrows=n_samples)
        
            for t in range(file_length):
                data = np.empty(shape=(1, 100000))
                data[0,:] = analyze_nmdata(device.get_adc())[1]
                
                if t % 1000 == 0:
                    pbar.update(file_number * file_length + t)
                    
    #             if not np.any(data[0,:] < 8465):
    #                 continue
    # #             else:
    # #                 plt.clf()
    # #                 plt.plot(data[0,:])
    # #                 plt.show()
    
                waveforms.append(data)
                waveforms.flush()
    
                time.sleep(0.005)

    pbar.finish()


def consecutive(data, max_stepsize=10):  # Returns group of consecutive increasing values
    return np.split(data, np.where(np.diff(data) > max_stepsize)[0] + 1)


def gauss(x, mean, sigma, amp):
    return amp * np.exp( - (x - mean)*(x - mean) / (2 * sigma * sigma))

# @profile
def analyze_data(files):
    amplitudes = np.empty(shape=1)

    for filename in files:
        with tb.open_file(filename) as data_file:
            for dataset in data_file.root.event_data[:5000]:
#                 dataset = medfilt(dataset.astype(np.int16), 5)
#                 plt.plot(dataset)
#                 plt.show()
                hist, mids = np.histogram(dataset[::5], bins=np.arange(np.floor(np.min(dataset)) - 0.5, np.ceil(np.max(dataset)) + 0.5, 1))
                mids += 0.5
                
                coeff, _ = curve_fit(gauss, mids[:-1], hist[:], p0=(np.mean(dataset), 3, 5000), sigma=10, absolute_sigma=True)
                mean, sigma = coeff[0], coeff[1]

#                 del hist, mids

#                 plt.bar(mids[:-1], hist, 1)
#                 plt.plot(mids[:-1], gauss(mids[:-1], *coeff), 'r-')
#                 plt.show()                

                amplitudes = _get_amplitudes(dataset, mean, sigma, amplitudes)

    amplitudes = amplitudes[1:]

    return amplitudes


def analyze_fast(files):
    amplitudes = np.empty(shape=1)

    for filename in files:
        with tb.open_file(filename) as data_file:
            for dataset in data_file.root.event_data[:3500]:
#                 dataset = medfilt(dataset.astype(np.int16), 5)
                plt.plot(dataset, '-')
                plt.ylabel('Signal / ADC units')
                plt.xlabel('Time')
                plt.show()
                reset_peak_indices = np.arange(18, 99928, 1030)
#                 print reset_peak_indices

#                 del hist, mids

#                 plt.bar(mids[:-1], hist, 1)
#                 plt.plot(mids[:-1], gauss(mids[:-1], *coeff), 'r-')
#                 plt.show()                

                amplitudes = _store_amplitudes(reset_peak_indices, dataset, amplitudes)

    amplitudes = amplitudes[1:]

    return amplitudes



# @profile
def _get_amplitudes(dataset, mean, sigma, amplitudes):
# tweaking possibilities: distance between two hits and amplitude threshold
    if len(np.where(dataset > mean + 10 * sigma)[0]) != 0:
        reset_peaks = np.where(dataset > mean + 10 * sigma)[0]

        # indizes in dataset of falling edge of hit. 50 is minimum distance between two distinct hits
        reset_peak_indices = [reset_peaks[0]]
        reset_peak_indices = np.concatenate((reset_peak_indices, reset_peaks[np.where(np.diff(reset_peaks) > 900)[0] + 1]))
#                     print reset_peak_indices

#                     plt.plot(dataset, 'b.-')
#                     plt.plot(medfilt(dataset.astype(np.int16), 5), 'r.-')
#                     plt.show()
        amplitudes = _store_amplitudes(reset_peak_indices, dataset, amplitudes)
    return amplitudes

@njit
def _store_amplitudes(reset_peak_indices, dataset, amplitudes):
    for peak_index in reset_peak_indices[:-1]:
            amplitude = np.median(dataset[peak_index + 15:peak_index + 25]) - np.median(dataset[peak_index + 1010:peak_index + 1020])
            amplitudes = np.concatenate((amplitudes, np.array([amplitude])))
    return amplitudes


def plot_spectrum(amplitudes_arr):
    if len(amplitudes_arr) == 1:
        alpha = 1
    else:
        alpha = .5

    for amplitudes in amplitudes_arr:
        print 'hits: ', len(amplitudes)
#         amplitudes = 0.43 * amplitudes  # convert to mV

        plt.hist(amplitudes, bins=np.arange(np.floor(np.amin(amplitudes)) - 0.5, np.ceil(np.amax(amplitudes)) + 0.5, bin_width), label='todo', alpha=alpha)
        hist, edges = np.histogram(amplitudes, bins=np.arange(np.floor(np.min(amplitudes)) - 0.5, np.ceil(np.max(amplitudes)) + 0.5, bin_width))

#     plt.xlabel('Amplitude / mV')
    plt.ylabel('Counts')
#     plt.ylim(0, 1000)
#     plt.legend(loc=0)
    plt.show()

    return hist, edges


def fit_tb_spectrum(hist, edges):
    mids = edges + 0.5

    from pylandau import langau
    def spectrum_func(x, mu, eta, sigma, A):
        return langau(x, mu, eta, sigma, A)

    coeff, pcov = curve_fit(spectrum_func, mids[62:-1], hist[62:], p0=(40, 2, 1, 100), sigma=10, absolute_sigma=True, bounds=([-np.inf, 1, -np.inf, -np.inf], [np.inf, np.inf, np.inf, np.inf]))
    print coeff

    plt.bar(mids[:-1], hist, align='center', width=1)
    plt.ylim(0, 1500)

#     plt.plot(mids[:-1], langau(mids[:-1], *coeff), 'g-', linewidth=1.5)
#     plt.plot(mids[62:-1], spectrum_func(mids[62:-1], *coeff), "r-", linewidth=3)
    plt.xlabel('Amplitude / mV')
    plt.ylabel('Counts')
    plt.show()


def fit_spectrum(hist, edges):
    mids = (edges + 0.5)

    def gauss(x, mean, sigma, amp):
        return amp * np.exp( - (x - mean)*(x - mean) / (2 * sigma * sigma))
    
    plot_range = np.arange(mids[0], mids[-1], 0.1)

    coeff, _ = curve_fit(gauss, mids[11:-1], hist[11:], p0=(12, .5, 300), sigma=2, absolute_sigma=True)
    print 'peak:', coeff
    
    coeff_2, _ = curve_fit(gauss, mids[:10], hist[:10], p0=(0, 1, 20000), sigma=5, absolute_sigma=True)
    print 'pedestal:', coeff_2

    plt.bar(mids[:-1], hist, align='center', width=bin_width)
#     plt.ylim(0, 3000)
#     plt.xlabel('Amplitude / mV')
    plt.ylabel('Counts')
    plt.plot(plot_range, gauss(plot_range, *coeff), "r-", linewidth=3)
    plt.plot(plot_range, gauss(plot_range, *coeff_2), "r-", linewidth=3)
    plt.show()


if __name__== "__main__":
    base_path = '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/'

#     bias_60_files = [base_path + 'testbeam_data_dec16/single_px/bias60/bias60_pt00.h5',
#                      base_path + 'testbeam_data_dec16/single_px/bias60/bias60_pt01.h5']
#
    bias_40_files = [base_path + 'testbeam_data_dec16/single_px/bias40/bias40_pt00.h5',
                     base_path + 'testbeam_data_dec16/single_px/bias40/bias40_pt01.h5']
# 
#     bias_30_files = [base_path + 'testbeam_data_dec16/single_px/bias30/bias30_pt00.h5',
#                      base_path + 'testbeam_data_dec16/single_px/bias30/bias30_pt01.h5']
# 
#     bias_20_files = [base_path + 'testbeam_data_dec16/single_px/bias20/bias20_pt00.h5',
#                      base_path + 'testbeam_data_dec16/single_px/bias20/bias20_pt01.h5']
#
#     wo_source = [base_path + 'test_data/single_px/40000_without_source_pt00.h5',
#                  base_path + 'test_data/single_px/40000_without_source_pt01.h5']

    test_data = [base_path + 'test_data/single_px/5000_fe_source_8-41_pt00.h5']
    
    fe_data = [base_path + 'test_data/single_px/fe_source/100000_fe_source_pt00.h5',
               base_path + 'test_data/single_px/fe_source/100000_fe_source_pt01.h5',
               base_path + 'test_data/single_px/fe_source/100000_fe_source_pt02.h5',
               base_path + 'test_data/single_px/fe_source/100000_fe_source_pt03.h5']

    am_data = [base_path + 'test_data/single_px/1000000_am_source_pt00.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt01.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt02.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt03.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt04.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt05.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt06.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt07.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt08.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt09.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt10.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt11.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt12.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt13.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt14.h5',
               base_path + 'test_data/single_px/1000000_am_source_pt15.h5']

#     from multiprocessing import Pool
# 
#     pool = Pool(2)
#     result = pool.map(analyze_data, [test_files])
#     pool.close()
#     amplitudes = result[0]

    overwrite = True
    filename = 'amplitudes_fe_source_8-41.npy'
    bin_width = 1.

    start = time.time()

    if not overwrite and os.path.isfile(filename):
        logging.info('File already exists, abort.')
    else:
#         pass
        amplitudes = analyze_fast(fe_data)
#         np.save(base_path + 'test_data/single_px/fe_source/' + filename, amplitudes)
#     stop = time.time()

#     print stop - start
    amplitudes = np.load(base_path + 'test_data/single_px/fe_source/amplitudes_fe_source_8-41.npy')
    print len(amplitudes)
    hist, edges = plot_spectrum([amplitudes])
    fit_spectrum(hist, edges)
