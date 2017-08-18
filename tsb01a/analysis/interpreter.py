import numpy as np
import tables as tb
import logging
import progressbar
from numba import njit

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s')


class Tsb01aInterpreter(object):
    def __init__(self, input_files, col_n, row_n, div=12):
        self.input_files = input_files
        self.col_n = col_n
        self.row_n = row_n
        self.div = div

    def interpret_data(self, output_file):
        # output_file = self.input_files[0][:-7] + "interpreted.h5"

        f_n = 12  # TODO make a better guess according to col_n,row_n,..etc
        f_nn = f_n - 1
        chunk_size = 1000

        hit_dtype = np.dtype([("bl", "i8", (self.col_n, self.row_n)), ("sig", "i8", (self.col_n, self.row_n))])
        hit = np.empty(f_nn * chunk_size, dtype=hit_dtype)

        with tb.open_file(output_file, "w") as out_file_h5:
            description = np.zeros((1,), dtype=hit_dtype).dtype
            hit_table = out_file_h5.create_table(out_file_h5.root,
                                                 name="Images",
                                                 description=description,
                                                 title='image_data',
                                                 filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))

            for file_number, input_file in enumerate(self.input_files):
                logging.info("Interpreting input file %d of %d" % (file_number + 1, len(self.input_files)))
                with tb.open_file(input_file) as in_file_h5:
                    pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ',
                                                            progressbar.Bar(marker='#', left='|', right='|'), ' ',
                                                            progressbar.AdaptiveETA()],
                                                   maxval=len(in_file_h5.root.event_data), poll=10, term_width=80)
                    pbar.start()

                    end = len(in_file_h5.root.event_data)
                    slice_start = 0
                    while slice_start < end:
                        slice_end = min(slice_start + chunk_size, end)
                        raw_array = in_file_h5.root.event_data[slice_start:slice_end]
                        hit = _mk_img(raw_array, hit, self.col_n, self.row_n, self.div)
                        hit_table.append(hit)
                        hit_table.flush()
                        slice_start = slice_end
                        pbar.update(slice_end)
                    pbar.finish()

    def create_hit_table(self, input_file, output_file, threshold=0):
        hit_dtype = np.dtype([("event_number", "u8"), ("frame", "u1"), ("column", "u2"), ("row", "u2"), ("charge", "i2")])
        description = np.zeros((1,), dtype=hit_dtype).dtype

        logging.info("Start creating hit table")

        chunk_size = 1000  # 6 kb per frame

        with tb.open_file(input_file, "r") as in_file_h5:
            n_frames = in_file_h5.root.Images.shape[0]
            pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ',
                                                    progressbar.Bar(marker='#', left='|', right='|'), ' ',
                                                    progressbar.AdaptiveETA()],
                                           maxval=n_frames, poll=10, term_width=80)
            pbar.start()
            start_event = 0
            with tb.open_file(output_file, "w") as out_file_h5:
                hit_table = out_file_h5.create_table(out_file_h5.root,
                                                     name="Hits",
                                                     description=description,
                                                     title="Hit data",
                                                     filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))

                n_pixel = in_file_h5.root.Images[0]["bl"].shape[0] * in_file_h5.root.Images[0]["bl"].shape[1]
                max_hit_per_frame = chunk_size * n_pixel
                hits = np.zeros(shape=(max_hit_per_frame, ), dtype=hit_dtype)

                for i in range(0, n_frames, chunk_size):
                    pbar.update(i)
                    data = in_file_h5.root.Images[i:i + chunk_size]

                    max_index = _get_hit_info(hits, data, start_event, threshold, chunk_size)
#                     print np.count_nonzero(hits['event_number'])
#                     hits_rec = np.core.records.fromarrays(hits.transpose(),
#                                                           names='event_number, frame, column, row, charge')#,
#                                                           #formats=hit_dtype.
#                                                           #'<u8, <u1, <u2, <u2, <i2')
                    hit_table.append(hits[:max_index])
                    hit_table.flush()
                start_event += i

            pbar.finish()

        logging.info("Hit table created")

        return


# Helper functions that use njit for faster computation
@njit
def _mk_img(raw_array, res, col_n, row_n, div):
    n_rows = 12
    n_cols = col_n + 1
    reset = 10#             col_i, row_i = col_indices[hit_index], row_indices[hit_index]
#             hits['event_number'][hit_index] = index
#             hits['frame'][hit_index] = frame
#             # Col/row start at 1 by convention
#             hits['column'][hit_index] = col_i + 1
#             hits['row'][hit_index] = row_i + 1
#             hits['charge'][hit_index] = amplitudes[col_i, row_i]
    delay = 10
    exp = 50

    r1_off = div * 3 + 6
    r1_len = div * 2 * col_n
    r0_off = r1_off + r1_len + (reset + delay + 3) * div

    row_offset = div
    r_len = r0_off + r1_len + 6

    f_off = 0
    f_len = (div * (
        2 * 32 + reset + delay + 2 * 32 + 3) + 1 + exp + 3) * div  # TODO calc from col_n,row_n,exposure...

    dat = np.empty(len(raw_array[0, :]) * 2, dtype=np.int16)
    res_i = 0
    for raw_i in range(len(raw_array)):
        # convert raw to adc data
        dat_i = 0
        for r in raw_array[raw_i, :]:
            if r & 0xE0000000 == 0x20000000:
                dat[dat_i] = r & 0x00003fff
                dat[dat_i + 1] = (r & 0x0fffc000) >> 14
                dat_i = dat_i + 2

        # get valid data (baseline and signal)
        frame_n = len(dat) / f_len
        for i in range(frame_n):
            # select relevant data for i-th frame
            frame_data = dat[f_off + i * f_len:f_off + (i + 1) * f_len]
            for j in range(row_n):
                row_data = frame_data[row_offset + j * r_len:row_offset + (j + 1) * r_len]
                r1_dat = row_data[r1_off:r1_off + r1_len]
                r0_dat = row_data[r0_off:r0_off + r1_len]
                for k in range(col_n):
                    if i != frame_n - 1:
                        res[res_i + i]["bl"][k, j] = np.median(r0_dat[k * div * 2:(k + 1) * div * 2][2:-1])
                    if i != 0:
                        res[res_i + i - 1]["sig"][k, j] = np.median(r1_dat[k * div * 2:(k + 1) * div * 2][2:-1])
        res_i = res_i + i
    return res[:res_i]


@njit
def _get_hit_info(hits, data, start_event, threshold, chunk_size):
    frame = 0  # No subframe info set to 0
    n_hits = 0
    hit_index = 0

    for index in range(chunk_size):
        amplitudes = data[index]["bl"] - data[index]["sig"]

        hit_indices = np.where(amplitudes > threshold)
        col_indices, row_indices = hit_indices[0], hit_indices[1]

        for i in range(len(col_indices)):
            if hits.shape[0] <= hit_index:
                raise IndexError('Hit array too small to store hits. Decrease chunk size or increase hit array size.')
            col_i, row_i = col_indices[i], row_indices[i]
            event_number = start_event + hit_index
            hits[hit_index]['event_number'] = event_number
            hits[hit_index]['frame'] = frame
            # Col/row start at 1 by convention
            hits[hit_index]['column'] = col_i
            hits[hit_index]['row'] = row_i + 1
            hits[hit_index]['charge'] = amplitudes[col_i, row_i]
            hit_index = hit_index + 1

    return hit_index


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 1:
        input_files = [sys.argv[1]]
    else:
        input_files = ['example.h5']

    interpreter = Tsb01aInterpreter(input_files, col_n=31, row_n=12, div=12)

    interpreter.interpret_data()
    interpreter.create_hit_table(input_file=input_files[0][:-3] + "interpreted.h5",
                                 output_file=input_files[0][:-3] + "Hits.h5",
                                 threshold=1)
