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

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #../
sys.path.append( root_dir + "/tsb01a" ) 

import tsb01


class TestSim(unittest.TestCase):

            
    def setUp(self):

        cocotb_compile_and_run(
            [root_dir + '/tests/tsb01_tb.v'], 
            sim_bus='basil.utils.sim.SiLibUsbBusDriver',
            include_dirs = (root_dir,)
            )
                
        with open(root_dir + '/tsb01a/tsb01.yaml', 'r') as f:
            cnfg = yaml.load(f)
            
        cnfg['transfer_layer'][0]['type'] = 'SiSim'
        cnfg['hw_drivers'][0]['init']['no_calibration'] = True
       
        self.dut = tsb01.tsb01(yaml=cnfg)
       
    def test(self):
        self.dut.init()
        
       
    def tearDown(self):
        self.my_qmca.dut.close()
        time.sleep(5)
        cocotb_compile_clean()

if __name__ == '__main__':
    unittest.main()