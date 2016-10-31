
#
# ------------------------------------------------------------
# Copyright (c) All rights reserved 
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#

from basil.dut import Dut
import numpy as np
import time
import logging

np.set_printoptions(formatter={'int':hex})

dut = Dut('tsb01.yaml')
dut.init()

dut['VDD'].set_current_limit(100, unit='mA')
dut['VDD'].set_voltage(1.8, unit='V')
dut['VDD'].set_enable(True)

adc_ch = 'fadc0_rx'

dut[adc_ch].reset()
dut[adc_ch].set_delay(10)
dut[adc_ch].set_data_count(10)
dut[adc_ch].set_single_data(True)
dut[adc_ch].set_en_trigger(False)
    
dut['DATA_FIFO'].reset()

for i in range(10):
    pattern = 10 + i * 100
    dut['fadc_conf'].enable_pattern(pattern)  

    dut[adc_ch].start()
    while not dut[adc_ch].is_done():
        pass

    lost = dut[adc_ch].get_count_lost()
    data = dut['DATA_FIFO'].get_data() 
    data = data & 0x3fff
    if data.tolist() != [pattern]*10 or lost !=0 :
        logging.error("Wrong ("+str(hex(pattern))+") or lost data :" + str(data) + " Lost: " + str(lost))
    else:
        logging.info("OK Data:" + str(data) + " Lost: " + str(lost))
