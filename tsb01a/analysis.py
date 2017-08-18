import numpy as np
from matplotlib import pyplot as plt
import tables as tb
import time
import logging
from scipy.optimize import curve_fit
import progressbar
import pylandau


def plot_calibrated_spectrum(amplitudes, row, col, show_plots=False):
    single_amplitudes = amplitudes[:, row, col]
#     print len(single_amplitudes)
#     plt.hist(single_amplitudes, bins=np.arange(np.floor(np.min(single_amplitudes)) - 0.5, np.ceil(np.max(single_amplitudes)) + 0.5, 1))
#     plt.show()

    hist, edges = np.histogram(single_amplitudes, bins=np.arange(-100, 25000, 200))

#     hist, edges = np.histogram(single_amplitudes, bins=25)
    if show_plots:
        plt.title('Pixel col: %s row: %s' % (col, row))
        plt.bar(edges[:-1] + 100, hist, align='center', width=200, alpha=1, color='b')
        plt.show()

#     print np.sum(hist)

    return hist, edges


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
        one_pixel_amplitudes = amplitudes[:, index[0], index[1]]  # - pedestal['mean']
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
                                           formats='<i4, <u1, <u2, <u2, <u4')

    del array

    with tb.open_file('/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/Hits_calibrated.h5', 'w') as out_file:
        #         hit_table = out_file.create_table(where=out_file.root, title='Hit information', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False), expectedrows=len(hit_table), obj=hit_table)
        #         hit_table = out_file.create_table(where=out_file.root, obj=hit_table)
        hits = out_file.create_table(out_file.root,
                                     name='Hits',
                                     title='Hits',
                                     description=hit_table.dtype,
                                     filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))
        hits.append(hit_table)

    return


calibration_file = '/media/silab/8420f8d2-80d9-4742-a6ab-998a7d6522b3/test_data/imaging/fe_source/16x12_flavor2_calibration.npz'
hit_file = '/media/tsb01a_data/testbeam_data_mar17/imaging/v_bias_40/amplitudes_raw.npy'

calibration_file = np.load(calibration_file)
amplitudes = np.load(hit_file)

amplitudes = amplitudes[:, :, 16:32]

calibration = calibration_file['calibration']
offset = calibration_file['offset']

calibrated = amplitudes

for index in np.arange(len(amplitudes)):
    calibrated[index] = (amplitudes[index] - offset) * calibration / 3.62

plot_calibrated_spectrum(calibrated, row=8, col=5, show_plots=True)


# Create h5 File with calibrated data
# hits = get_hits(calibrated, 4000)
# create_hit_table(hits)
