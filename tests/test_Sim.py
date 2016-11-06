#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#

import unittest
from basil.dut import Dut
from basil.utils.sim.utils import cocotb_compile_and_run, cocotb_compile_clean
import yaml
import os
import sys
import time
import sys
import numpy as np

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #../
sys.path.append( root_dir + "/tsb01a" ) 

import tsb01


class TestSim(unittest.TestCase):


    def setUp(self):

        cocotb_compile_and_run(
            [root_dir + '/tests/tsb01_tb.v'], 
            sim_bus='basil.utils.sim.SiLibUsbBusDriver',
            include_dirs = (root_dir + '/firmware/src',)
            )
   
        with open(root_dir + '/tsb01a/tsb01.yaml', 'r') as f:
            cnfg = yaml.load(f)

        cnfg['transfer_layer'][0]['type'] = 'SiSim'
        cnfg['hw_drivers'][0]['init']['no_calibration'] = True

        self.dut = tsb01.tsb01(yaml=cnfg)


    def test(self):
        self.dut.init()
#         self.dut.sel_all()

        self.dut.sel_one(row=10, col=25, howmuch=100)
            
        for ch in ['fadc0_rx','fadc1_rx','fadc2_rx','fadc3_rx']:
            self.dut[ch].reset()
            self.dut[ch].set_delay(10)
            self.dut[ch].set_data_count(10)
            self.dut[ch].set_single_data(True)
            self.dut[ch].set_en_trigger(False)
            self.dut[ch].start()

        for _ in range(500):
            tmp = self.dut['OUTA2'].is_done()

        data = self.dut['DATA_FIFO'].get_data() 
        self.assertTrue(len(data) == 4*10)
        
        exp = [0]*10 + [0x20003fff]*10 + [0x40003fffL]*10 + [0x60000000L]*10 
        self.assertTrue(data.tolist() == exp)
        
        self.assertTrue(self.dut['SPI_FADC'].get_data().tolist() == [3,0])
        
        
    def tearDown(self):
        self.dut.close()
        time.sleep(5)
        cocotb_compile_clean()

if __name__ == '__main__':
    unittest.main()
