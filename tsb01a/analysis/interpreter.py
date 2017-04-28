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

    def interpret_data(self):
        output_file = self.input_files[0][:-7] + "interpreted.h5"

        f_n = 12  # TODO make a better guess according to col_n,row_n,..etc
        f_nn = f_n - 1
        chunk_size = 1000

        hit_dtype = np.dtype([("bl", "f8", (self.col_n, self.row_n)), ("sig", "f8", (self.col_n, self.row_n))])
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
        hit_dtype = np.dtype([("event_number", "u8"), ("frame", "u1"), ("column", "u2"), ("row", "u2"), ("charge", "u4")])
        description = np.zeros((1,), dtype=hit_dtype).dtype

        logging.info("Start creating hit table")

        with tb.open_file(input_file, "r") as in_file_h5:
            with tb.open_file(output_file, "w") as out_file_h5:
                hit_table = out_file_h5.create_table(out_file_h5.root,
                                                     name="Hits",
                                                     description=description,
                                                     title="Hit data",
                                                     filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False))

                for index, image in enumerate(in_file_h5.root.Images[:]):
                    amplitudes = image["bl"] - image["sig"]
                    amplitudes = amplitudes.astype(np.int64)

                    hits = _get_hit_info(amplitudes, 1, index)
                    hits_rec = np.core.records.fromarrays(hits.transpose(),
                                                          names='event_number, frame, column, row, charge',
                                                          formats='<u8, <u1, <u2, <u2, <u4')
                    hit_table.append(hits_rec)

                    hit_table.flush()

        logging.info("Hit table created")

        return


# Helper functions that use njit for faster computation
@njit
def _mk_img(raw_array, res, col_n, row_n, div):
    n_rows = 12
    n_cols = col_n + 1
    reset = 10
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
def _get_hit_info(amplitudes, threshold, index):
    hit_indices = np.where(amplitudes > threshold)

    col_indices, row_indices = hit_indices[0], hit_indices[1]

    hits = np.zeros(shape=(len(col_indices), 5))

    for hit_index in range(len(col_indices)):
        col = col_indices[hit_index]
        row = row_indices[hit_index]
        charge = amplitudes[col, row]
        hits[hit_index] = (index, 0, col, row, charge)

    return hits


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
