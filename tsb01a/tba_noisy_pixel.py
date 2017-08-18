'''Example script to run a full analysis with high resolution telescope data + a fast time reference plane + a small device under tests.

The telescope consists of 6 Mimosa26 planes and one FE-I4 with a full size planar n-in-n sensor as a timing reference.
The device under tests is a small passive sensor in LFoundry 150 nm CMOS process.

The Mimosa26 has an active area of 21.2mm x 10.6mm and the pixel matrix consists of 1152 columns and 576 rows (18.4um x 18.4um pixel size).
The total size of the chip is 21.5mm x 13.7mm x 0.036mm (radiation length 9.3660734)
The matrix is divided into 4 areas. For each area the threshold can be set up individually.
The quartes are from column 0-287, 288,575, 576-863 and 864-1151.

The timing reference is about 2 cm x 2 cm divided into 80 x 336 pixels. The time stamping happens with a 40 MHz clock (25 ns).

MIMOSA CONVERTER: python ex_simple_converter.py -tr -ow m26_telescope_scan.h5


'''

import logging
import numpy as np
import tables as tb

import matplotlib.pyplot as plt


from testbeam_analysis import hit_analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")


def run_analysis():
    # The location of the example data files, one file per DUT
    data_file = r'/media/tsb01a_data/testbeam_data_apr17/100um/v_bias_40/Hits.h5'

    # Pixel dimesions and matrix size of the DUTs
    pixel_size = (20, 20)  # (Column, row) pixel pitch in um
    # switched col/row for M26 because transpose option
    n_pixels = (31, 12)  # (Column, row) dimensions of the pixel matrix
    z_positions = [0.]  # in um
    dut_name = "TSB_01_A"  # Friendly names for plotting

# #     Generate noisy pixel mask
#     hit_analysis.generate_pixel_mask(threshold=0.5,
#                                      input_hits_file=data_file,
#                                      n_pixel=n_pixels,
#                                      pixel_mask_name="NoisyPixelMask",
#                                      pixel_size=pixel_size,
#                                      dut_name=dut_name,
#                                      filter_size=5)

    with tb.open_file(data_file[:-3] + '_noisy_pixel_mask.h5') as in_file:
        for flavor in range(2):
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
                min_hit_charge=10,
                max_hit_charge=500,
                column_cluster_distance=2,
                row_cluster_distance=2,
                frame_cluster_distance=0,
                dut_name=dut_name,
                plot=True,
                chunk_size=1000000)

            # Plot cluster charge
            with tb.open_file(data_file[:-3] + '_clustered.h5', "r") as in_file_h5:
                cluster = in_file_h5.root.Cluster[:]
                sel = np.logical_and(cluster['n_hits'] < 2,
                                     cluster['n_hits'] < 2)

                print cluster['seed_column'].min(), cluster['seed_column'].max()
#                 cluster = cluster[sel]
                plt.clf()
                plt.hist(cluster['charge'], range=(0, 500), bins=100)
                plt.show()


if __name__ == '__main__':  # Main entry point is needed for multiprocessing under windows
    run_analysis()
