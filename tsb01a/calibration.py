from __future__ import division

import numpy as np
import tables as tb
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt

config = {'energy': 5898}


def plot_single_spectrum(amplitudes, row, col, show_plots=False):
    single_amplitudes = amplitudes[:,row,col]
#     print len(single_amplitudes)
#     plt.hist(single_amplitudes, bins=np.arange(np.floor(np.min(single_amplitudes)) - 0.5, np.ceil(np.max(single_amplitudes)) + 0.5, 1))
#     plt.show()
    
    hist, edges = np.histogram(single_amplitudes, bins=np.arange(np.floor(np.min(single_amplitudes)) - 0.5, np.ceil(np.max(single_amplitudes)) + 0.5, 1))

#     hist, edges = np.histogram(single_amplitudes, bins=25)
    if show_plots:
        plt.title('Pixel col: %s row: %s' %(col, row))
        plt.bar(edges[:-1] + .5, hist, align='center', width=1, alpha=1, color='b')
        plt.show()
    
#     print np.sum(hist)
    
    return hist, edges


def plot_calibrated_spectrum(amplitudes, row, col, show_plots=False):
    single_amplitudes = amplitudes[:,row,col]
#     print len(single_amplitudes)
#     plt.hist(single_amplitudes, bins=np.arange(np.floor(np.min(single_amplitudes)) - 0.5, np.ceil(np.max(single_amplitudes)) + 0.5, 1))
#     plt.show()
    
    hist, edges = np.histogram(single_amplitudes, bins=np.arange(-1050, 3050, 100))

#     hist, edges = np.histogram(single_amplitudes, bins=25)
    if show_plots:
        plt.title('Pixel col: %s row: %s' %(col, row))
        plt.bar(edges[:-1] + 50, hist, align='center', width=100, alpha=1, color='b')
        plt.show()
    
#     print np.sum(hist)
    
    return hist, edges


def fit_spectrum(amplitudes, show_plots=False):
    
    hist, edges = np.histogram(amplitudes, bins=np.arange(-50 - 0.5, 50 + 0.5, 1))
    
    mids = (edges + .5)


    def gauss(x, mean, sigma, amp):
        return amp * np.exp( - (x - mean)*(x - mean) / (2 * sigma * sigma))

#     print hist[np.where(hist == np.amax(hist))[0]]

    if show_plots:
        pass
#         plt.bar(mids[:-1], hist, align='center', width=1)
#         plt.show()

    
    ped_index = np.where(hist == np.amax(hist))[0][0]
    ped_mean = mids[np.where(hist == np.amax(hist))[0][0]]
    peak_index = np.where(np.diff(hist) > 5)[0][-1]
    peak_mean = mids[np.where(np.diff(hist) > 5)[0][-1]]

#     print peak_mean

#     plt.bar(mids[:-1], hist, align='center', width=1)
#     plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), ped_mean, .8, np.amax(hist)) + gauss(np.arange(mids[0], mids[-1], 0.1), peak_mean, 1., 0.027 * np.amax(hist)), "r-", linewidth=2, label='initial guess')
#     plt.xlim(-5, 20)

    try:
        ped_coeff, _ = curve_fit(gauss, mids[ped_index - 10:ped_index + 10], hist[ped_index - 10:ped_index + 10], p0=(ped_mean, .8, np.amax(hist)), sigma=None, absolute_sigma=True)
    
#         plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *ped_coeff) + gauss(np.arange(mids[0], mids[-1], 0.1), peak_mean, 1., 0.027 * np.amax(hist)), "m-", linewidth=2, label='between fits')

        lower_bound = np.argwhere(mids > ped_coeff[0] + 4 * ped_coeff[1])[0][0]
#         print mids[lower_bound:peak_index + 20]
        
        test = np.amax([lower_bound, peak_index -10])

        peak_coeff, _ = curve_fit(gauss, mids[test:peak_index + 20], hist[test:peak_index + 20], p0=(peak_mean, 1., 0.027 * np.amax(hist)), sigma=None, absolute_sigma=True)


#         plt.plot(np.arange(mids[0], mids[-1], 0.1), gauss(np.arange(mids[0], mids[-1], 0.1), *ped_coeff) + gauss(np.arange(mids[0], mids[-1], 0.1), *peak_coeff), "g-", linewidth=2, label='after fits')
#         plt.legend()
#         plt.show()
        
    # TODO: better error handling
    except RuntimeError:
        print 'Error occured'
        plt.legend(loc=0)
        plt.show()
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}
    except ValueError:
        print 'Error occured'
        plt.legend(loc=0)
        plt.show()

        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

 
#         return {'mean': ped_mean, 'sigma': 2, 'amp': 0}, {'mean': 0.027 * np.amax(hist), 'sigma': 0, 'amp': 0}
    except TypeError:
        print 'Error occured'
        plt.legend(loc=0)
        plt.show()
        return {'mean': 0, 'sigma': 2, 'amp': 0}, {'mean': 0, 'sigma': 0, 'amp': 0}

 
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


def calibrate_pixel(amplitudes, show_plots=False):
    """ Calculates factor for conversion from ADC units to eV for given pixel """
        
    pedestal, peak = fit_spectrum(amplitudes, show_plots)
    peak_distance = np.abs(peak['mean'] - pedestal['mean'])
    offset = pedestal['mean']
    
#     print config['energy'] / peak_distance
    
    return config['energy'] / peak_distance, offset


def calibrate(amplitudes):
    
    calibration = np.zeros((amplitudes.shape[1], amplitudes.shape[2]))
    offset = np.zeros((amplitudes.shape[1], amplitudes.shape[2]))

    for index, _ in np.ndenumerate(calibration):
#         print index[0], index[1]
        if index[0] == 11 and index[1] == 46:
            show_plots=True
        else:
            show_plots=False
        calibration[index[0], index[1]], offset[index[0], index[1]] = calibrate_pixel(amplitudes[:, index[0], index[1]], show_plots)
        
    return calibration, offset


def read_amplitudes(filename):
    return np.load(filename)


def get_hits(amplitudes, threshold):
    """
    Iterate over all pixels to determine threshold for hit and calculate number of hits in this pixel
    """

    # Prepare hits array to be filled and to generate indices  
    hit_map = np.zeros((amplitudes.shape[1], amplitudes.shape[2]))

    # Create array with event numbers
    hits = np.zeros((amplitudes.shape[1], amplitudes.shape[2], len(amplitudes)))

    for index, _ in np.ndenumerate(hit_map):
#         hist, edges = plot_single_spectrum(amplitudes, index[0], index[1])
        one_pixel_amplitudes = amplitudes[:, index[0], index[1]] # - pedestal['mean']
        one_pixel_amplitudes[one_pixel_amplitudes < threshold] = 0

        # Create hit array where non-hits have been set to 0 and amplitude is preserved
        hits[index[0], index[1]] = one_pixel_amplitudes

        # Create hit array where number of hits are counted with setting all hits to 1
#         one_pixel_amplitudes[one_pixel_amplitudes >= pedestal['mean'] + 3 * pedestal['sigma']] = 1
        hit_map[index[0], index[1]] = np.sum(one_pixel_amplitudes, axis=0)

    hits = np.transpose(hits, axes=(2, 0, 1))

    return hits


def create_hit_table(hits):
#     event_numbers = np.arange(0, len(amplitudes), 1)

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
                                             formats = '<i4, <u1, <u2, <u2, <u2')

    del array

    with tb.open_file('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/47x12_50000_Hits_calibrated.h5', 'w') as out_file:
#         hit_table = out_file.create_table(where=out_file.root, title='Hit information', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False), expectedrows=len(hit_table), obj=hit_table)
#         hit_table = out_file.create_table(where=out_file.root, obj=hit_table)
        hits = out_file.create_table(out_file.root,
                                      name='Hits',
                                      title='Calibrated Hits',
                                      description=hit_table.dtype,
                                      filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
        hits.append(hit_table)

    return


if __name__== "__main__":
    amplitudes = read_amplitudes('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/amplitudes_47x12_50000.npy')
    
    charge = amplitudes[:,:,16:32]
    
    plot_single_spectrum(charge, row=3, col=1, show_plots=True)
    plt.show()
    
    calibration, offset = calibrate(charge)
    
    print calibration
    calibrated = charge
    
    for index in np.arange(len(charge)):
        calibrated[index] = (charge[index] - offset) * calibration / 3.62
    
    print calibrated
    
    plot_calibrated_spectrum(calibrated, row=3, col=1, show_plots=True)
    
    np.save('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/16x12_flavor2_calibrated.npy', calibrated)
    
    np.savez('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/16x12_flavor2_calibration.npz', calibration=calibration, offset=offset)
    
    in_volt = charge * 24e-6
    
    np.save('/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/16x12_flavor2_volt.npy', in_volt)

#     for i in range(12):
#         plot_single_spectrum(calibrated * 24, row=i, col=1, show_plots=True)
#     plt.show()

    hits = get_hits(calibrated, 1000)
#     create_hit_table(hits)
    