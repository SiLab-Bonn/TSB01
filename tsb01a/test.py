import tsb01
from matplotlib import pyplot as plt
import numpy as np
import time
import progressbar

# initialize FPGA
device = tsb01.tsb01()
device.init()

#device.sel_one()
#device.init_adc(howmuch=100)

device['OUTA1'].set_data_count(100)
device['OUTA1'].set_single_data(True)
device['OUTA1'].set_en_trigger(False)

device['DATA_FIFO'].reset()


device['OUTA1'].start()

# self[ch].set_data_count(1000000)

single = False
nmdata = device['DATA_FIFO'].get_data()
print nmdata

# data = device['DATA_FIFO'].get_data()
# while not (device['OUTA1'].is_done() and device['OUTA2'].is_done()):
#     print device['DATA_FIFO'].get_data()

for i, _ in enumerate(nmdata):
    print hex(nmdata[i]), hex(nmdata[i]& 0x3fff)