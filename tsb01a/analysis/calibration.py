from __future__ import division

import numpy as np
import tables as tb
import progressbar
from numba import njit
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt

config = {'energy': 5898}


def fit_spectrum(charge, show_plots=False, number=0):
    hist, edges = np.histogram(charge, bins=np.arange(-15, 150, 1))

    def gauss(x, amp, mu, sigma):
        return amp * np.exp(- (x - mu) * (x - mu) / (2 * sigma * sigma))

    # Use rising slope of pedestal peak and 2 bins of falling slope to fit peak
    fit_range_pedestal = np.where(hist == np.max(hist))[0][0]

    # search in range +/- 3 from guessed peak for maximum
    # fit_range_peak = signal_range[0] + np.where(signal == np.max(signal))[0][0]
    fit_range_peak = fit_range_pedestal + 4

    if show_plots:
        plt.clf()

        plt.title(number)
        print('fit number %s' % number)
        plt.bar(edges[:-1], hist, width=1, fill=False, edgecolor='C0')
        plt.plot(edges[:-1], hist, 'C0.', label="Data")
        # plt.plot([edges[fit_range_pedestal - 8], edges[fit_range_pedestal - 8]], [0, 10000], 'C1')
        # plt.plot([edges[fit_range_pedestal + 1], edges[fit_range_pedestal + 1]], [0, 10000], 'C1')
        # plt.plot([edges[fit_range_peak], edges[fit_range_peak]], [0, 10000], 'C3')
        # plt.plot([edges[fit_range_peak + 25], edges[fit_range_peak + 25]], [0, 10000], 'C3')

    try:
        # fit pedestal
        popt_pedestal, _ = curve_fit(gauss, edges[fit_range_pedestal - 8:fit_range_pedestal + 1],
                                     hist[fit_range_pedestal - 8:fit_range_pedestal + 1],
                                     p0=(np.amax(hist), edges[fit_range_pedestal], 2.))

        peak_guess = edges[fit_range_peak] + np.where(np.amax(hist[fit_range_peak: fit_range_peak + 25]) == hist[fit_range_peak: fit_range_peak + 25])[0][0]
        print peak_guess

        # fit peak
        popt_peak, _ = curve_fit(gauss,
                                 edges[fit_range_peak:fit_range_peak + 25],
                                 hist[fit_range_peak: fit_range_peak + 25],
                                 p0=(np.amax(hist[fit_range_peak: fit_range_peak + 25]), peak_guess, 1.))

        if show_plots:
            plot_x = np.arange(-10, 150, 0.01)

            # plt.bar(edges[:-1], hist, width=1, fill=False, edgecolor='C0')
            # plt.plot(edges[:-1], hist, 'C0.', label="Data")
            plt.plot(plot_x, gauss(plot_x, *popt_pedestal), 'C1', label="Pedestal Fit")
            plt.plot(plot_x, gauss(plot_x, *popt_peak), 'C3', label="Peak fit")
            plt.legend()
            plt.ylim(0, 10000)
            plt.xlim(-5, 20)
            # plt.yscale('log')
            plt.ylim(ymin=0.01)

            print np.abs(popt_peak[1] - popt_pedestal[1])

            plt.show()

            return np.abs(popt_peak[1] - popt_pedestal[1])

    except:
        print 'EXCEPTION'
        plot_x = np.arange(-10, 150, 0.01)
        plt.plot(plot_x, gauss(plot_x, np.amax(hist), edges[fit_range_pedestal], 2.), 'C1', label="Pedestal Guess")
        plt.plot(plot_x, gauss(plot_x, np.amax(hist[fit_range_peak: fit_range_peak + 25]), peak_guess, 1.), 'C3', label="Peak Guess")
        plt.legend()
        plt.ylim(0, 10000)
        plt.xlim(-5, 20)
        # plt.yscale('log')
        plt.ylim(ymin=0.01)

        plt.show()
        return np.abs(edges[fit_range_pedestal] - peak_guess)

    return np.abs(popt_peak[1] - popt_pedestal[1])


def get_pixel_data(input_file, col=None, row=None):
    with tb.open_file(input_file) as in_file_h5:
        hits = in_file_h5.root.Hits[:]
        if col or row:
            selected_pixel = np.where(np.logical_and(hits["column"] == col, hits["row"] == row))[0]

            return hits[selected_pixel]
        else:
            return hits


def get_pixel_data_all(input_files, col, row):
    hit_dtype = np.dtype([("event_number", "u8"), ("frame", "u1"), ("column", "u2"), ("row", "u2"), ("charge", "i4")])
    all_hits = np.zeros((1,), dtype=hit_dtype)

    for input_file in input_files:
        with tb.open_file(input_file) as in_file_h5:
            hits = in_file_h5.root.Hits[:]
            # selected_pixel = np.where(np.logical_and(hits["column"] == col, hits["row"] == row))[0]
            # all_hits = np.append(all_hits, hits[selected_pixel])
            all_hits = np.append(all_hits, hits)

    return hits[1:]

@njit
def hist_hits(hits, hist, n_pixel_x, n_pixel_y, max_charge):
    for hit in hits:
        col_i, row_i, charge_i = hit["column"] - 1, hit["row"] - 1, hit["charge"] - 1
        if col_i >= n_pixel_x:
            raise IndexError("Exceeding histogram size in x, please increase size.")
        if row_i >= n_pixel_y:
            raise IndexError("Exceeding histogram size in y, please increase size.")
        if charge_i < max_charge:
            hist[col_i, row_i, charge_i] =+ 1


def histogram_hits(hit_file, output_file, n_pixel_x, n_pixel_y, max_charge=256, chunk_size=100000):
    if max_charge > 2**8:
        raise IndexError("Max enrties per bin should not exceed 256")
    
    with tb.open_file(hit_file, "r") as in_file_h5:
        n_hits = in_file_h5.root.Hits.shape[0]
        with tb.open_file(output_file, "w") as out_file_h5:
            hit_hist = out_file_h5.create_carray(out_file_h5.root, name='HistHits', atom = tb.UInt16Atom(),
                                                 shape=(n_pixel_x, n_pixel_y, max_charge),
                                                 filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
            hit_hist[:] = 0
            pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ',
                                                        progressbar.Bar(marker='#', left='|', right='|'), ' ',
                                                        progressbar.AdaptiveETA()],
                                               maxval=n_hits, poll=10, term_width=80)
            pbar.start()
            
            hist = np.zeros(shape=(n_pixel_x, n_pixel_y, max_charge), dtype=np.uint8)
    
            for i in range(0, n_hits, chunk_size):
                pbar.update(i)
                hits = in_file_h5.root.Hits[i:i + chunk_size]
                hist_hits(hits, hist, n_pixel_x, n_pixel_y, max_charge)
            
            hit_hist[:] = hist
            
            pbar.finish()

def calibrate(input_file, n_cols, n_rows):
    hits = get_pixel_data(input_file)
    output_file = input_file[:-3] + 'calibrated.h5'
    number = 1

    for index, _ in np.ndenumerate(np.empty(shape=(n_cols, n_rows))):
        charge = hits[np.where(np.logical_and(hits["column"] == index[0], hits["row"] == index[1]))[0]]["charge"]
        adc_distance = fit_spectrum(charge, True, number)
        charge = charge * 1. / adc_distance * config["energy"]
        hits[np.where(np.logical_and(hits["column"] == index[0], hits["row"] == index[1]))[0]]["charge"] = charge
        number += 1

    with tb.open_file(output_file, "w") as out_file_h5:
        with tb.open_file(input_file, "r") as in_file_h5:
            hit_table = out_file_h5.create_table(out_file_h5.root,
                                                 name="Hits calibrated",
                                                 description=in_file_h5.description,
                                                 title="Hit data",
                                                 filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
            hit_table.append(hits)
