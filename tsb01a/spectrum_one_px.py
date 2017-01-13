from matplotlib import pyplot as plt
import numpy as np
import tables as tb
import time
import progressbar
import os.path
import logging

from scipy.signal import medfilt
from numba import jit, njit

# import tsb01

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

def analyze_data(files):
    amplitudes = np.empty(shape=1)

    for filename in files:
        with tb.open_file(filename) as data_file:
            for dataset in data_file.root.event_data[:]:
#                 dataset = medfilt(dataset.astype(np.int16), 5)
#                 plt.plot(dataset)
#                 plt.show()
                hist, edges = np.histogram(dataset, bins=np.arange(np.floor(np.min(dataset)) - 0.5, np.ceil(np.max(dataset)) + 0.5, 1))
                mids = edges + 0.5

                model = Model(gauss)
                pars = model.make_params(amp=25000, mean=np.mean(dataset[::10]), sig=2.)

                result = model.fit(hist, pars, x=mids[:-1])
                mean = result.params['mean'].value
                sigma = result.params['sig'].value

#                 print result.fit_report()
#                 plt.plot(mids[:-1], result.best_fit, 'r-')
#                 plt.bar(edges[:-1], hist, 1)
#                 plt.show()

                amplitudes = _get_amplitudes(dataset, mean, sigma, amplitudes)

    amplitudes = amplitudes[1:]

    return amplitudes


def _get_amplitudes(dataset, mean, sigma, amplitudes):
# tweaking possibilities: distance between two hits and amplitude threshold
    if len(np.where(dataset > mean + 10 * sigma)[0]) != 0:
        reset_peaks = np.where(dataset > mean + 10 * sigma)[0]

        # indizes in dataset of falling edge of hit. 50 is minimum distance between two distinct hits
        reset_peak_indices = reset_peaks[0]
        reset_peak_indices = np.append(reset_peak_indices, reset_peaks[np.where(np.diff(reset_peaks) > 950)[0] + 1])
#                     print reset_peak_indices

#                     plt.plot(dataset, 'b.-')
#                     plt.plot(medfilt(dataset.astype(np.int16), 5), 'r.-')
#                     plt.show()
        for peak_index in reset_peak_indices:
            if peak_index <= 15 or peak_index >= 99000:
                continue
#                     plt.plot(dataset)
#                     plt.show()

            amplitude = np.mean(dataset[peak_index + 18:peak_index + 23]) - np.mean(dataset[peak_index + 1000:peak_index + 1010])
            amplitudes = np.append(amplitudes, amplitude)
    return amplitudes


def plot_spectrum(amplitudes_arr):
    if len(amplitudes_arr) == 1:
        alpha = 1
    else:
        alpha = .5

    for amplitudes in amplitudes_arr:
        print 'hits: ', len(amplitudes)

        plt.hist(amplitudes, bins=np.arange(np.floor(np.amin(amplitudes)) - 0.5, np.ceil(np.amax(amplitudes)) + 0.5, 1), label='todo', alpha=alpha)
        hist, edges = np.histogram(amplitudes, bins=np.arange(np.floor(np.min(amplitudes)) - 0.5, np.ceil(np.max(amplitudes)) + 0.5, 1))

    plt.xlabel('Amplitude / ADC units')
    plt.ylabel('Counts')
    plt.ylim(0, 1000)
    plt.legend(loc=0)
    plt.show()

    return hist, edges


def fit_spectrum(hist, edges):
    mids = edges + 0.5

    from pylandau import langau
    def spectrum_func(x, mu, eta, sigma, A):
        return langau(x, mu, eta, sigma, A)

    coeff, pcov = curve_fit(spectrum_func, mids[62:-1], hist[62:], p0=(40, 2, 1, 100), sigma=10, absolute_sigma=True, bounds=([-np.inf, 1, -np.inf, -np.inf], [np.inf, np.inf, np.inf, np.inf]))
    print coeff

    plt.bar(mids[:-1], hist, align='center', width=1)
    plt.ylim(0, 1000)

    plt.plot(mids[:-1], langau(mids[:-1], *coeff), 'g-', linewidth=1.5)
    plt.plot(mids[62:-1], spectrum_func(mids[62:-1], *coeff), "r-", linewidth=3)
    plt.show()


def double_gauss(x, a1, m1, s1, a2, m2, s2):
    return a1 * np.exp( - (x - m1)*(x - m1) / (2 * s1 * s1)) + a2 * np.exp( - (x - m2)*(x - m2) / (2 * s2 * s2))


def gauss(x, amp, mean, sig):
    return amp * np.exp( - (x - mean)*(x - mean) / (2 * sig * sig))


def mpv(x, amp, mean, sig, a, offset):
    return amp * np.exp( - (x - mean)*(x - mean) / (2 * sig * sig)) + a * (x - offset) * (x - offset) 


if __name__== "__main__":
    base_path = '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/'
    
#     bias_60_files = [base_path + 'testbeam_data_dec16/single_px/bias60/bias60_pt00.h5',
#                      base_path + 'testbeam_data_dec16/single_px/bias60/bias60_pt01.h5']

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
#
#     from multiprocessing import Pool
# 
#     pool = Pool(2)
#     result = pool.map(analyze_data, [test_files])
#     pool.close()
#     amplitudes = result[0]

    amplitudes_40 = analyze_data(bias_40_files)

    np.save('amplitudes_40.npy', amplitudes_40)

#     amplitudes_30 = np.load('amplitudes_30.npy')
# 
# 
#     hist, edges = plot_spectrum([amplitudes_30])

#     fit_spectrum(hist, edges)
