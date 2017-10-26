'''

'''

import logging
import numpy as np
import tables as tb

import matplotlib.pyplot as plt


from testbeam_analysis import hit_analysis
from tsb01a.analysis import interpreter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")


def run_analysis(data_file):

    # Pixel dimesions and matrix size of the DUT
    pixel_size = (20, 20)  # (column, row) pixel pitch in um
    n_pixels = (15, 12)  # (column, row) dimensions of the pixel matrix
    dut_name = "TSB01_A"  # Friendly names for plotting

    inter = interpreter.Tsb01aInterpreter(None, 31, 12, 12)
    inter.create_hit_table(input_file='/media/tsb01a_data/testbeam_data_apr17/700um/v_bias_40/bias_40_interpreted.h5',
                                 output_file=data_file[:-3] + '_calibrated_tmp.h5',
                                 start_col=17,
                                 threshold=30,
                                 calibrate=True,
                                 calibration_file='/media/tsb01a_data/x-ray-tube-27_09/tb_700/calibration.h5')
 
    inter.shift_columns(input_file=data_file[:-3] + '_calibrated_tmp.h5',
                        output_file=data_file[:-3] + '_calibrated.h5',
                        shift=-16)

#     Generate noisy pixel mask
    hit_analysis.generate_pixel_mask(threshold=1,
                                     input_hits_file=data_file[:-3] + '_calibrated.h5',
                                     n_pixel=n_pixels,
                                     pixel_mask_name="NoisyPixelMask",
                                     pixel_size=pixel_size,
                                     dut_name=dut_name,
                                     filter_size=3)

    with tb.open_file(data_file[:-3] + '_calibrated_noisy_pixel_mask.h5') as in_file:
        for flavor in range(1):
            print(flavor)
            with tb.open_file(data_file[:-3] + '_calibrated_disable_pixel_mask_f%d.h5' % flavor, 'w') as out_file:
                disable = out_file.create_carray(out_file.root, name='DisabledPixelMask',
                                                 shape=in_file.root.NoisyPixelMask.shape,
                                                 atom=in_file.root.NoisyPixelMask.atom)
                disable[:] = True

                if flavor == 0:
                    disable[:16] = False
#                     disable[9, 9] = True
#                     disable[10, 9] = True
                elif flavor == 1:
                    disable[16:16 + 15] = False
                    
                print disable
#
            # Cluster hits
            hit_analysis.cluster_hits(
                create_cluster_hits_table=True,
                input_hits_file=data_file[:-3] + '_calibrated.h5',
                input_noisy_pixel_mask_file=data_file[:-3] + '_calibrated_noisy_pixel_mask.h5',
                input_disabled_pixel_mask_file=data_file[:-3] + '_calibrated_disable_pixel_mask_f%d.h5' % flavor,
                min_hit_charge=0,
                max_hit_charge=200000,
                column_cluster_distance=1,
                row_cluster_distance=1,
                frame_cluster_distance=0,
                dut_name=dut_name,
                plot=True,
                chunk_size=1000000)
# 
# 
# def plot_cluster_charge(data_file):
# 
#     # Plot cluster charge
#     with tb.open_file(data_file[:-3] + '_clustered.h5', "r") as in_file_h5:
#         cluster = in_file_h5.root.Cluster[:]
#         sel = np.logical_and(cluster['n_hits'] < 2,
#                              cluster['is_edge_cluster'] == 0)
# 
#         cluster = cluster[sel]
#         plt.clf()
#         plt.hist(cluster['charge'] / 1000, range=(0, 200), bins=100)
#         plt.xlabel('Energy / keV')
#         plt.ylabel('Hits')
#         plt.show()


def fit_charge_spectrum(data_file):
    from scipy.optimize import curve_fit
    import pylandau

    with tb.open_file(data_file[:-3] + '_calibrated_clustered.h5', "r") as in_file_h5:
        cluster = in_file_h5.root.Cluster[:]
        sel = np.logical_and(cluster['n_hits'] < 2,
                             cluster['is_edge_cluster'] == 0)

    cluster = cluster[sel]

    hist, edges = np.histogram(cluster["charge"], range=(30, 100), bins=np.arange(29.5, 100.5, 1))
    mids = edges[:-1] + 0.5

    coeff, _ = curve_fit(pylandau.langau, mids[10:], hist[10:],
                         sigma=np.sqrt(mids[10:]),
                         absolute_sigma=True,
                         p0=(60, 1, 4, 11000),
                         bounds=(1, 15000))

    x = np.arange(0, 200, 0.1)

    plt.bar(mids, hist, width=1)
    plt.plot(x, pylandau.langau(x, *coeff), 'C1-', linewidth=1.5)
    plt.xlabel('Energy / keV')
    plt.ylabel('Hits')
    plt.xlim(xmin=0)
    plt.show()

    # calculate reduced chi squared
    chi2 = np.sum((hist - pylandau.langau(mids, *coeff)) * (hist - pylandau.langau(mids, *coeff)) / (np.std(hist) * np.std(hist)))
    print('reduced chi2 is {0:.4f}').format(chi2 / 4)
    print(coeff)


if __name__ == '__main__':  # Main entry point is needed for multiprocessing under windows
    # The location of the example data files, one file per DUT
    data_file = r'/media/tsb01a_data/testbeam_data_apr17/700um/v_bias_40/Hits.h5'
    run_analysis(data_file)
#     plot_cluster_charge(data_file)
    fit_charge_spectrum(data_file)
