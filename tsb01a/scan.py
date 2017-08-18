import tsb01
from time import sleep
import tables as tb
import logging
import numpy as np

class scan(object):
    def __init__(self, n_data_points, clk_divide):
        self.n_data_points = n_data_points
        self.clk_divide = clk_divide
        
        self.device = tsb01.tsb01()
        self.device.init()

        
    def record_data(self, filename, n_framesets):
        self.device.sel_all(howmuch=self.n_data_points, divide=self.clk_divide)
        sleep(.1)
        
        with tb.open_file(filename, 'w') as data_file:
            logging.info('Create file %s' % filename)
            # TODO: check if file exists
            waveforms = data_file.create_earray(data_file.root, name='event_data', atom=tb.UIntAtom(), shape=(0, self.n_data_points), title='The raw events from the ADC', filters=tb.Filters(complib='blosc', complevel=5, fletcher32=False), expectedrows=n_framesets)

            # Record given amount of data
            if n_framesets:
                for frameset in xrange(n_framesets):
                    data = np.empty(shape=(1, self.n_data_points))

                    data[0,:] = self.device.get_adc()[1]
                    waveforms.append(data)
                    waveforms.flush()

            # TODO allow data taking until stop
            