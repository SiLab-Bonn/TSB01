'''

'''

import logging
import numpy as np
import tables as tb

import matplotlib.pyplot as plt


from testbeam_analysis import hit_analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")


def run_analysis(data_file):

    # Pixel dimesions and matrix size of the DUT
    pixel_size = (20, 20)  # (column, row) pixel pitch in um
    n_pixels = (15, 12)  # (column, row) dimensions of the pixel matrix
    dut_name = "TSB01_A"  # Friendly names for plotting

#     Generate noisy pixel mask
    hit_analysis.generate_pixel_mask(threshold=0.5,
                                     input_hits_file=data_file,
                                     n_pixel=n_pixels,
                                     pixel_mask_name="NoisyPixelMask",
                                     pixel_size=pixel_size,
                                     dut_name=dut_name,
                                     filter_size=3)

    with tb.open_file(data_file[:-3] + '_noisy_pixel_mask.h5') as in_file:
        for flavor in range(1):
            with tb.open_file(data_file[:-3] + '_disable_pixel_mask_f%d.h5' % flavor, 'w') as out_file:
                disable = out_file.create_carray(out_file.root, name='DisabledPixelMask',
                                                 shape=in_file.root.NoisyPixelMask.shape,
                                                 atom=in_file.root.NoisyPixelMask.atom)
                disable[:] = True

                if flavor == 0:
                    disable[:16] = False
                elif flavor == 1:
                    disable[16:16 + 15] = False

            # Cluster hits
            hit_analysis.cluster_hits(
                create_cluster_hits_table=True,
                input_hits_file=data_file,
                input_noisy_pixel_mask_file=data_file[:-3] + '_noisy_pixel_mask.h5',
                input_disabled_pixel_mask_file=data_file[:-3] + '_disable_pixel_mask_f%d.h5' % flavor,
                min_hit_charge=0,
                max_hit_charge=200000,
                column_cluster_distance=1,
                row_cluster_distance=1,
                frame_cluster_distance=0,
                dut_name=dut_name,
                plot=True,
                chunk_size=500000)


def plot_cluster_charge(data_file):

    # Plot cluster charge
    with tb.open_file(data_file[:-3] + '_clustered.h5', "r") as in_file_h5:
        cluster = in_file_h5.root.Cluster[:]
        sel = np.logical_and(cluster['n_hits'] < 2,
                             cluster['is_edge_cluster'] == 0)

        cluster = cluster[sel]
        plt.clf()
        plt.hist(cluster['charge'] / 1000, range=(0, 200), bins=100)
        plt.xlabel('Energy / keV')
        plt.ylabel('Hits')
        plt.show()


def fit_charge_spectrum(data_file):
    from scipy.optimize import curve_fit
    import pylandau

    with tb.open_file(data_file[:-3] + '_clustered.h5', "r") as in_file_h5:
        cluster = in_file_h5.root.Cluster[:]
        sel = np.logical_and(cluster['n_hits'] < 2,
                             cluster['is_edge_cluster'] == 0)

        cluster = cluster[sel]

        hist, edges = np.histogram(cluster["charge"] / 1000, range=(0, 200), bins=np.arange(-0.5, 200.5, 1))
        mids = edges[:-1] + 0.5

        coeff, _ = curve_fit(pylandau.langau, mids, hist,
                             sigma=10 * np.ones_like(mids),
                             absolute_sigma=True,
                             p0=(60, 5, 4, 8000),
                             bounds=(1, 10000))

        x = np.arange(-20, 220, 0.1)

        plt.bar(mids, hist, width=1)
        plt.plot(x, pylandau.langau(x, *coeff), 'C1-', linewidth=1.5)
        plt.show()

    # calculate reduced chi squared
    chi2 = np.sum((hist - pylandau.langau(mids, *coeff)) * (hist - pylandau.langau(mids, *coeff)) / (np.std(hist) * np.std(hist)))
    print('reduced chi2 is {0:.4f}').format(chi2 / 4)
    print(coeff)


if __name__ == '__main__':  # Main entry point is needed for multiprocessing under windows
    # The location of the example data files, one file per DUT
    data_file = r'/media/tsb01a_data/testbeam_data_apr17/700um/v_bias_40/Hits_altered.h5'
    run_analysis(data_file)
    plot_cluster_charge(data_file)
    fit_charge_spectrum(data_file)
