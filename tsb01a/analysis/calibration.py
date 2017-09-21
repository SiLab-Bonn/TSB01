from __future__ import division

import numpy as np
import tables as tb
import progressbar
from numba import njit
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt


def fit_spectrum(charge, distance_guess=4, show_plots=False, number=0, col=None, row=None):
    hist, edges = np.histogram(charge, bins=np.arange(-25.5, 150.5, 1))
    mids = edges + 0.5

    def gauss(x, amp, mu, sigma):
        return amp * np.exp(- (x - mu) * (x - mu) / (2 * sigma * sigma))

    # Use rising slope of pedestal peak and 2 bins of falling slope to fit peak
    fit_range_pedestal = np.where(hist == np.max(hist))[0][0]

    # search in range +/- 3 from guessed peak for maximum
    # fit_range_peak = signal_range[0] + np.where(signal == np.max(signal))[0][0]
    fit_range_peak = fit_range_pedestal + distance_guess

    peak_guess = mids[fit_range_peak] + np.where(np.amax(hist[fit_range_peak: fit_range_peak + 25]) == hist[fit_range_peak: fit_range_peak + 25])[0][0]

    # Method for fast computation of peka position using a guess and weighted average
#     counts = hist[fit_range_peak - 2: fit_range_peak + 10]
#     bin_positions = mids[fit_range_peak - 2: fit_range_peak + 10]
#
#     print bin_positions
#
#     fast_peak = np.average(bin_positions, weights=counts)
#     print "fast peak:", fast_peak

    plt.clf()

    if show_plots:
        plt.clf()

        if col or row:
            plt.title("Column: %d // Row: %d" % (col, row))
        plt.bar(mids[:-1], hist, width=1, fill=False, edgecolor='C0')
        plt.plot(mids[:-1], hist, 'C0.', label="Data")
        # plt.plot([fast_peak, fast_peak], [0, 2000], 'C3--', label="Average Peak")
        # plt.plot([edges[fit_range_pedestal - 8], edges[fit_range_pedestal - 8]], [0, 10000], 'C1')
        # plt.plot([edges[fit_range_pedestal + 1], edges[fit_range_pedestal + 1]], [0, 10000], 'C1')
        # plt.plot([edges[fit_range_peak], edges[fit_range_peak]], [0, 10000], 'C3')
        # plt.plot([edges[fit_range_peak + 25], edges[fit_range_peak + 25]], [0, 10000], 'C3')

    try:
        # fit pedestal
        popt_pedestal, _ = curve_fit(gauss, mids[fit_range_pedestal - 8:fit_range_pedestal + 1],
                                     hist[fit_range_pedestal - 8:fit_range_pedestal + 1],
                                     p0=(np.amax(hist), mids[fit_range_pedestal], 1.))

        # fit peak
        popt_peak, _ = curve_fit(gauss,
                                 mids[fit_range_peak:fit_range_peak + 15],
                                 hist[fit_range_peak: fit_range_peak + 15],
                                 p0=(np.amax(hist[fit_range_peak - 1: fit_range_peak + 15]), peak_guess, 1.))

        if show_plots:
            plot_x = np.arange(-10, 150, 0.01)

            # plt.bar(edges[:-1], hist, width=1, fill=False, edgecolor='C0')
            # plt.plot(edges[:-1], hist, 'C0.', label="Data")
            plt.plot(plot_x, gauss(plot_x, *popt_pedestal), 'C1', label="Pedestal Fit")
            plt.plot(plot_x, gauss(plot_x, *popt_peak), 'C3', label="Peak fit")
            plt.legend()
            plt.ylim(0, 2000)
            plt.xlim(-10, 100)
            # plt.yscale('log')
            plt.ylim(ymin=0.01)

            print np.abs(popt_peak[1])

            plt.show()
#             plt.savefig("./output_plots_cu/col_" + str(col).zfill(2) + "_row_" + str(row).zfill(2) + ".pdf")

        return np.abs(popt_peak[1])

    except Exception as excep:
        print excep

        plot_x = np.arange(-10, 150, 0.01)
        plt.plot(plot_x, gauss(plot_x, np.amax(hist), mids[fit_range_pedestal], 1.), 'C1', label="Pedestal Guess")
        plt.plot(plot_x, gauss(plot_x, np.amax(hist[fit_range_peak: fit_range_peak + 25]), peak_guess, 1.), 'C3', label="Peak Guess")
        plt.legend()
        plt.ylim(0, 2000)
        plt.xlim(-10, 100)
        # plt.yscale('log')
        plt.ylim(ymin=0.01)

        plt.show()
#         plt.savefig("./output_plots/col_" + str(col).zfill(2) + "_row_" + str(row).zfill(2) + ".pdf")
        return np.abs(popt_peak[1])

    return np.abs(popt_peak[1])


def plot_calibrated_spectrum(charge, distance_guess=4, show_plots=False):
    hist, edges = np.histogram(charge, bins=np.arange(-10.5, 40.5, 1))
    mids = edges + 0.5

    def gauss(x, amp, mu, sigma):
        return amp * np.exp(- (x - mu) * (x - mu) / (2 * sigma * sigma))

    # Use rising slope of pedestal peak and 2 bins of falling slope to fit peak
    fit_range_pedestal = np.where(hist == np.max(hist))[0][0]

    # search in range +/- 3 from guessed peak for maximum
    # fit_range_peak = signal_range[0] + np.where(signal == np.max(signal))[0][0]
    fit_range_peak = fit_range_pedestal + distance_guess

    peak_guess = mids[fit_range_peak] + np.where(np.amax(hist[fit_range_peak: fit_range_peak + 25]) == hist[fit_range_peak: fit_range_peak + 25])[0][0] + .5

    plt.clf()

    if show_plots:
        plt.clf()

        plt.bar(mids[:-1], hist, width=1, fill=False, edgecolor='C0')
        plt.plot(mids[:-1], hist, 'C0.', label="Data")
        # plt.plot([edges[fit_range_pedestal - 8], edges[fit_range_pedestal - 8]], [0, 10000], 'C1')
        # plt.plot([edges[fit_range_pedestal + 1], edges[fit_range_pedestal + 1]], [0, 10000], 'C1')
        # plt.plot([edges[fit_range_peak], edges[fit_range_peak]], [0, 10000], 'C3')
        # plt.plot([edges[fit_range_peak + 25], edges[fit_range_peak + 25]], [0, 10000], 'C3')
#         plt.show()

#     try:
        # fit pedestal
    popt_pedestal, _ = curve_fit(gauss, mids[fit_range_pedestal - 8:fit_range_pedestal + 1],
                                 hist[fit_range_pedestal - 8:fit_range_pedestal + 1],
                                 p0=(np.amax(hist), mids[fit_range_pedestal], 1.))

    # fit peak
    popt_peak, _ = curve_fit(gauss,
                             mids[fit_range_peak:fit_range_peak + 15],
                             hist[fit_range_peak:fit_range_peak + 15],
                             p0=(np.amax(hist[fit_range_peak - 1: fit_range_peak + 15]), peak_guess, 1.))

    if show_plots:
        plot_x = np.arange(-10, 150, 0.01)

        # plt.bar(edges[:-1], hist, width=1, fill=False, edgecolor='C0')
        # plt.plot(edges[:-1], hist, 'C0.', label="Data")
        plt.plot(plot_x, gauss(plot_x, *popt_pedestal), 'C1', label="Pedestal Fit")
        plt.plot(plot_x, gauss(plot_x, *popt_peak), 'C3', label="Peak fit")
        plt.legend()
        plt.ylim(0, 2000)
        plt.xlim(-10, 100)
        # plt.yscale('log')
        plt.ylim(ymin=0.01)

        print np.abs(popt_peak[1])

        plt.show()
        # plt.savefig("./output_plots_cu/col_" + str(col).zfill(2) + "_row_" + str(row).zfill(2) + ".pdf")
#
#     except Exception as e:
#         print e
#
#         plot_x = np.arange(-10, 150, 0.01)
#         plt.plot(plot_x, gauss(plot_x, np.amax(hist), edges[fit_range_pedestal], 1.), 'C1', label="Pedestal Guess")
#         plt.plot(plot_x, gauss(plot_x, np.amax(hist[fit_range_peak: fit_range_peak + 25]), peak_guess, 1.), 'C3', label="Peak Guess")
#         plt.legend()
#         plt.ylim(0, 2000)
#         plt.xlim(-10, 30)
#         # plt.yscale('log')
#         plt.ylim(ymin=0.01)
#
#         plt.show()
#
#         return

    return np.abs(popt_peak[1])


def get_distance_map(input_file, show_plots=False, distance_guess=4):
    hits = _get_pixel_data(input_file)
    hits = hits[hits["column"] > 16]
    shape = (len(np.unique(hits["column"])), len(np.unique(hits["row"])))
    distances = np.zeros(shape=(shape[1], shape[0]))
    for col in range(shape[0]):
        for row in range(shape[1]):
            selection = np.where(np.logical_and(hits["column"] == col + 1 + 16, hits["row"] == row + 1))
            charge = hits["charge"][selection]
            # row before col to preserve matrix dimensions
            distances[row, col] = fit_spectrum(charge, distance_guess, show_plots=show_plots, col=col + 1 + 16, row=row + 1)

    with tb.open_file(input_file[:-7] + 'calibration.h5', 'w') as out_file:
        out_file.create_array(out_file.root, 'calibration', distances, "Calibration data")

    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(distances, interpolation='nearest', aspect='equal')
    ax.set_title('Difference between signal and Noise')
    fig.colorbar(im)    # scale of vertical bar
    plt.show()

    return distances


def create_calibration(calibration_list, energies, output_file, show_plots=False):
    def line(x, m, b):
        return m * x + b

    with tb.open_file(calibration_list[0], 'r') as in_file:
        data = in_file.root.calibration[:]

    slope, offset = np.ones(shape=data.shape), np.zeros(shape=data.shape)
    print slope.shape
    data = np.zeros(shape=(len(calibration_list), data.shape[0], data.shape[1]))
    # start plotting here
    for index in range(len(calibration_list)):
        with tb.open_file(calibration_list[index], 'r') as in_file:
            data[index, :, :] = in_file.root.calibration[:]

    for col in range(data.shape[2]):
        for row in range(data.shape[1]):
            adc_u = data[:, row, col]

            popt, _ = curve_fit(line, adc_u, energies, p0=((energies[-1] - energies[0]) / (adc_u[-1] - adc_u[0]), 0.))
            print popt
            if show_plots:
                plt.clf()
                plt.title('Col %d / Row %d' % (col + 1, row + 1))
                plt.plot(adc_u, energies, 'bo')
                plt.plot(np.linspace(0, 25, 5), line(np.linspace(0, 25, 5), *popt), 'r--', label="Fit")
                plt.show()
            # row before col to preserve matrix dimensions
            slope[row, col], offset[row, col] = popt[0], popt[1]

    with tb.open_file(output_file, 'w') as out_file:
        out_file.create_array(out_file.root, 'slope', slope, "Slope data for calibration")
        out_file.create_array(out_file.root, 'offset', offset, "Offset data for calibration")

    return slope, offset

@njit
def hist_hits(hits, hist, n_pixel_x, n_pixel_y, max_charge):
    for hit in hits:
        col_i, row_i, charge_i = hit["column"] - 1, hit["row"] - 1, hit["charge"] - 1
        if col_i >= n_pixel_x:
            raise IndexError("Exceeding histogram size in x, please increase size.")
        if row_i >= n_pixel_y:
            raise IndexError("Exceeding histogram size in y, please increase size.")
        if charge_i < max_charge:
            hist[col_i, row_i, charge_i] = + 1


def histogram_hits(hit_file, output_file, n_pixel_x, n_pixel_y, max_charge=256, chunk_size=100000):
    if max_charge > 2**8:
        raise IndexError("Max entries per bin should not exceed 256")

    with tb.open_file(hit_file, "r") as in_file_h5:
        n_hits = in_file_h5.root.Hits.shape[0]
        with tb.open_file(output_file, "w") as out_file_h5:
            hit_hist = out_file_h5.create_carray(out_file_h5.root, name='HistHits', atom=tb.UInt16Atom(),
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


# Only meant to be called from other calibration functions
def _get_pixel_data(input_file, col=None, row=None):
    with tb.open_file(input_file) as in_file_h5:
        hits = in_file_h5.root.Hits[:]
        if col or row:
            selected_pixel = np.where(np.logical_and(hits["column"] == col, hits["row"] == row))[0]

            return hits[selected_pixel]
        else:
            return hits
