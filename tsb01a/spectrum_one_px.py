from matplotlib import pyplot as plt
import numpy as np
import tables as tb
import time
import progressbar
import os.path
import logging

import tsb01

from lmfit import Model
from lmfit.models import GaussianModel


def record_data(filename='waveform_data.h5', n_samples=5000, overwrite=False):
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
    device.sel_one(row=4, col=4, howmuch=1100)
#     device.sel_all(howmuch=100)

    with tb.open_file(filename, 'w') as out_file:
        logging.info('Starting measurement')
        waveforms = out_file.create_earray(out_file.root, name='event_data', atom=tb.UIntAtom(), shape=(0,1100), title='The raw events from the ADC', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False), expectedrows=n_samples)

        pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='#', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=n_samples, poll=10, term_width=80).start()

        for t in range(n_samples):
            data = np.empty(shape=(1, 1100))
            data[0,:] = device.get_adc()[0]
#             plt.plot(data[0,:])
#             plt.show()
            waveforms.append(data)
            waveforms.flush()

            time.sleep(0.005)

            if t % 10 == 0:
                pbar.update(t)

        pbar.finish()


def read_data(filename='waveform_data.h5'):
    with tb.open_file(filename) as data_file:
        logging.info('Read data file %s' %filename)
        return data_file.root.event_data[:]


def plot_spectrum(data):
    first_mean = np.mean(data[:,45:65], axis=1)
    last_mean = np.mean(data[:,1020:1040], axis=1)
    
#     last_mean = np.mean(data[:,6:12], axis=1)
#     first_mean = np.mean(data[:,30:40], axis=1)

    amplitude = first_mean - last_mean

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.hist(amplitude, bins=np.arange(np.floor(np.min(amplitude)) - 0.5, np.ceil(np.max(amplitude)) + 0.5, 0.1))
    hist, edges = np.histogram(amplitude, bins=np.arange(np.floor(np.min(amplitude)) - 0.5, np.ceil(np.max(amplitude)) + 0.5, 0.1))
#     plt.yscale('log')
#     plt.ylim(0, 50)
    plt.xlabel('Amplitude / ADC units')
    plt.ylabel('Counts')
    plt.show()

    return hist, edges


def fit_spectrum(hist, edges):
    mids = edges + 0.05
  
    model = Model(double_gauss)
    pars = model.make_params(a1=30000, m1=1, s1=1, a2=10, m2=16, s2=1)

    result = model.fit(hist, pars, x=mids[:-1])
  
    plt.plot(mids[:-1], result.best_fit, 'r-')
    plt.bar(edges[:-1], hist, 0.1)

    print result.fit_report()

    plt.show()


def double_gauss(x, a1, m1, s1, a2, m2, s2):
    return a1 * np.exp( - (x - m1)*(x - m1) / (2 * s1 * s1)) + a2 * np.exp( - (x - m2)*(x - m2) / (2 * s2 * s2))


if __name__== "__main__":
#     record_data('./waveform_data/fe55_150000samples_better_res.h5', 150000, overwrite=False)

    data = read_data('./waveform_data/fe55_150000samples_better_res.h5')
 
    hist, edges = plot_spectrum(data)
    
    fit_spectrum(hist, edges)
