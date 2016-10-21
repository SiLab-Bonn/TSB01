#
# ------------------------------------------------------------
# Copyright (c) SILAB , Physics Institute of Bonn University
# ------------------------------------------------------------
#
# SVN revision information:
#  $Rev:: 15                    $:
#  $Author:: themperek          $:
#  $Date:: 2013-09-18 10:25:20 #$:
#

from basil.dut import Dut
import numpy as np
import matplotlib.pyplot as plt
import time, sys, os, string

class logger:
    def __init__(self, logfile="tsb01.log"):
        self.logfile = logfile
        self.stdout = True

    def append(self, output):
        if self.stdout:
            print output
        output = string.join(output.split("\n"), ",")
        with open(self.logfile, 'a') as f:
            f.write("%s\n" % output)

    def archive(self):
        with open('scan_archive.txt', 'a') as fo:
            try:
                with open(self.logfile) as f:
                    for line in f:
                        fo.write(line)
                os.remove(self.logfile)
            except:
                pass

class tsb01(Dut):
    def __init__(self, yaml="tsb01.yaml"):
        super(tsb01, self).__init__(yaml)
        self.l = logger()
        self.debug = 0
        self.howmuch = 10000
        self.divide = 1


    def init(self):
        super(tsb01, self).init()
        self.power()


    def power(self, pwr_en=True, VDDA=1.5, VDD=1.5, RST_VOL=0.8, FADC_VREF=0.88, IBIAS_COLBUF=1, IBIAS_CHIPBUF=-10):
        self['VDDA'].set_current_limit(100, unit='mA')
        
        self['VDDA'].set_voltage(VDDA, unit='V')
        self['VDDA'].set_enable(pwr_en)
        
        self['VDD'].set_voltage(VDD, unit='V')
        self['VDD'].set_enable(pwr_en)

        self['RST_VOL'].set_voltage(RST_VOL, unit='V')
        self['FADC_VREF'].set_voltage(FADC_VREF, unit='V')
        
        self['IBIAS_COLBUF'].set_current(IBIAS_COLBUF, unit='uA')
        self['IBIAS_CHIPBUF'].set_current(IBIAS_CHIPBUF, unit='uA')
        
        time.sleep(1)
        self.status()


    def status(self):
        s = 'VDD: %fV %fmA\n' % (self['VDD'].get_voltage(unit='V'), self['VDD'].get_current())    
        s = s + 'VDDA: %fV %fmA\n' % (self['VDDA'].get_voltage(unit='V'), self['VDDA'].get_current())
        s = s + 'RST_VOL: %fV %fmA\n' % (self['RST_VOL'].get_voltage(unit='V'), self['RST_VOL'].get_current())
        s = s + 'FADC_VREF: %fV %fmA\n' % (self['FADC_VREF'].get_voltage(unit='V'), self['FADC_VREF'].get_current())
        s = s + 'IBIAS_COLBUF: %fV %fmA\n' % (self['IBIAS_COLBUF'].get_voltage(unit='V'), self['IBIAS_COLBUF'].get_current())
        s = s + 'IBIAS_CHIPBUF: %fV %fmA\n' % (self['IBIAS_CHIPBUF'].get_voltage(unit='V'), self['IBIAS_CHIPBUF'].get_current())
        self.l.append(s)


    def sel_all(self, exp=100, delay0=10, repeat=1, howmuch=27998, reset=1, divide=4, trig_delay=10):  # 27898 data
        self["PULSE_DELAY"].reset()
        self['SEQ'].reset()
        self['SEQ'].clear()
        
        # TODO: t = clock_cycle?
        t = 0
        self['SEQ'].set_repeat_start(t)
        
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 0
        self['SEQ']['CLK_ROW_20'][t] = 0
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 0
        self['SEQ']['RST1_20'][t] = 0
        self['SEQ']['RST_EN_40'][t] = 0
        self['SEQ']['CLK_ROW_40'][t] = 0
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['RST2_40'][t] = 0
        self['SEQ']['RST1_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 0
        t = t + 1  
        # ## row reset
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 1
        self['SEQ']['CLK_ROW_20'][t] = 0
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 0
        self['SEQ']['RST1_20'][t] = 0          
        self['SEQ']['RST_EN_40'][t] = 1
        self['SEQ']['CLK_ROW_40'][t] = 0
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['RST2_40'][t] = 0
        self['SEQ']['RST1_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 0
        t = t + 1
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 1
        self['SEQ']['CLK_ROW_20'][t] = 1
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 0
        self['SEQ']['RST1_20'][t] = 0            
        self['SEQ']['RST_EN_40'][t] = 1
        self['SEQ']['CLK_ROW_40'][t] = 1
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['RST2_40'][t] = 0
        self['SEQ']['RST1_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 1
        t = t + 1
        self['SEQ'].set_nested_start(t)

        # ## read data
        for j in range(64):
            if j == 0:
                colin = 1
            else:
                colin = 0
            self['SEQ']['RST_EN_COL'][t] = colin
            self['SEQ']['CLK_COL'][t] = 0
            self['SEQ']['RST_EN_20'][t] = 0
            self['SEQ']['CLK_ROW_20'][t] = 0
            self['SEQ']['RST_ROW_20'][t] = 0
            self['SEQ']['RST2_20'][t] = 0
            self['SEQ']['RST1_20'][t] = 0
            self['SEQ']['RST_EN_40'][t] = 0
            self['SEQ']['CLK_ROW_40'][t] = 0
            self['SEQ']['RST_ROW_40'][t] = 0
            self['SEQ']['RST2_40'][t] = 0
            self['SEQ']['RST1_40'][t] = 0
            self['SEQ']['ADC_SYNC'][t] = 0
            t = t + 1
            self['SEQ']['RST_EN_COL'][t] = colin
            self['SEQ']['CLK_COL'][t] = 1
            self['SEQ']['RST_EN_20'][t] = 0
            self['SEQ']['CLK_ROW_20'][t] = 0
            self['SEQ']['RST_ROW_20'][t] = 0
            self['SEQ']['RST2_20'][t] = 0
            self['SEQ']['RST1_20'][t] = 0         
            self['SEQ']['RST_EN_40'][t] = 0
            self['SEQ']['CLK_ROW_40'][t] = 0
            self['SEQ']['RST_ROW_40'][t] = 0
            self['SEQ']['RST2_40'][t] = 0
            self['SEQ']['RST1_40'][t] = 0
            self['SEQ']['ADC_SYNC'][t] = 0
            t = t + 1
            
        # ## reset 
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 0
        self['SEQ']['CLK_ROW_20'][t] = 0
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 0
        self['SEQ']['RST1_20'][t] = 0
        self['SEQ']['RST_EN_40'][t] = 0
        self['SEQ']['CLK_ROW_40'][t] = 0
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['RST2_40'][t] = 0
        self['SEQ']['RST1_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 0
        t = t + 1
        self['SEQ']['RST_EN_COL'][t:t + reset] = 0
        self['SEQ']['CLK_COL'][t:t + reset] = 0
        self['SEQ']['RST_EN_20'][t:t + reset] = 0
        self['SEQ']['CLK_ROW_20'][t:t + reset] = 0
        self['SEQ']['RST_ROW_20'][t:t + reset] = 1
        self['SEQ']['RST2_20'][t:t + reset] = 0
        self['SEQ']['RST1_20'][t:t + reset] = 0   
        self['SEQ']['RST_EN_40'][t:t + reset] = 0
        self['SEQ']['CLK_ROW_40'][t:t + reset] = 0
        self['SEQ']['RST_ROW_40'][t:t + reset] = 1
        self['SEQ']['RST2_40'][t:t + reset] = 0
        self['SEQ']['RST1_40'][t:t + reset] = 0
        self['SEQ']['ADC_SYNC'][t:t + reset] = 0
        t = t + reset
        self['SEQ']['RST_EN_COL'][t:t + delay0] = 0
        self['SEQ']['CLK_COL'][t:t + delay0] = 0
        self['SEQ']['RST_EN_20'][t:t + delay0] = 0
        self['SEQ']['CLK_ROW_20'][t:t + delay0] = 0
        self['SEQ']['RST_ROW_20'][t:t + delay0] = 0
        self['SEQ']['RST2_20'][t:t + delay0] = 0
        self['SEQ']['RST1_20'][t:t + delay0] = 0
        self['SEQ']['RST_EN_40'][t:t + delay0] = 0
        self['SEQ']['CLK_ROW_40'][t:t + delay0] = 0
        self['SEQ']['RST_ROW_40'][t:t + delay0] = 0
        self['SEQ']['RST2_40'][t:t + delay0] = 0
        self['SEQ']['RST1_40'][t:t + delay0] = 0
        self['SEQ']['ADC_SYNC'][t:t + delay0] = 0        
        t = t + delay0
        
        # # read baseline
        for j in range(64):
            if j == 0:
                colin = 1
            else:
                colin = 0
            self['SEQ']['RST_EN_COL'][t] = colin
            self['SEQ']['CLK_COL'][t] = 0
            self['SEQ']['RST_EN_20'][t] = 0
            self['SEQ']['CLK_ROW_20'][t] = 0
            self['SEQ']['RST_ROW_20'][t] = 0
            self['SEQ']['RST2_20'][t] = 0
            self['SEQ']['RST1_20'][t] = 0
            self['SEQ']['RST_EN_40'][t] = 0
            self['SEQ']['CLK_ROW_40'][t] = 0
            self['SEQ']['RST_ROW_40'][t] = 0
            self['SEQ']['RST2_40'][t] = 0
            self['SEQ']['RST1_40'][t] = 0
            self['SEQ']['ADC_SYNC'][t] = 0
            t = t + 1
            self['SEQ']['RST_EN_COL'][t] = colin
            self['SEQ']['CLK_COL'][t] = 1
            self['SEQ']['RST_EN_20'][t] = 0
            self['SEQ']['CLK_ROW_20'][t] = 0
            self['SEQ']['RST_ROW_20'][t] = 0
            self['SEQ']['RST2_20'][t] = 0
            self['SEQ']['RST1_20'][t] = 0         
            self['SEQ']['RST_EN_40'][t] = 0
            self['SEQ']['CLK_ROW_40'][t] = 0
            self['SEQ']['RST_ROW_40'][t] = 0
            self['SEQ']['RST2_40'][t] = 0
            self['SEQ']['RST1_40'][t] = 0
            self['SEQ']['ADC_SYNC'][t] = 0
            t = t + 1
        # ## select next row
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 0
        self['SEQ']['CLK_ROW_20'][t] = 0
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 0
        self['SEQ']['RST1_20'][t] = 0          
        self['SEQ']['RST_EN_40'][t] = 0
        self['SEQ']['CLK_ROW_40'][t] = 0
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['RST2_40'][t] = 0
        self['SEQ']['RST1_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 0
        t = t + 1
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 0
        self['SEQ']['CLK_ROW_20'][t] = 1
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 0
        self['SEQ']['RST1_20'][t] = 0            
        self['SEQ']['RST_EN_40'][t] = 0
        self['SEQ']['CLK_ROW_40'][t] = 1
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['RST2_40'][t] = 0
        self['SEQ']['RST1_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 0
        t = t + 1
        self['SEQ'].set_nested_stop(t)
        ###########################     
        self['SEQ']['RST_EN_COL'][t:] = 0
        self['SEQ']['CLK_COL'][t:] = 0
        self['SEQ']['RST_EN_20'][t:] = 0
        self['SEQ']['CLK_ROW_20'][t:] = 0
        self['SEQ']['RST_ROW_20'][t:] = 0
        self['SEQ']['RST2_20'][t:] = 0
        self['SEQ']['RST1_20'][t:] = 0   
        self['SEQ']['RST_EN_40'][t:] = 0
        self['SEQ']['CLK_ROW_40'][t:] = 0
        self['SEQ']['RST_ROW_40'][t:] = 0
        self['SEQ']['RST2_40'][t:] = 0
        self['SEQ']['RST1_40'][t:] = 0
        self['SEQ']['ADC_SYNC'][t:] = 0
        self['SEQ'].set_wait(exp)
        self.init_adc(howmuch=howmuch)
        t = t + 1
        self['SEQ'].set_size(t)
        self['SEQ'].set_nested_repeat(96)
        self['SEQ'].set_clk_divide(divide)
        self['SEQ'].set_repeat(repeat)
        self['SEQ'].write(t)
        self.init_pulser(trig_delay=trig_delay)

        s = "sel_all exp:%d delay0:%d repeat:%d howmuch:%d reset:%d divide:%d" % (
                exp, delay0, repeat, howmuch, reset, divide)
        self.l.append(s)


    def sel_col(self, row=27, exp=100, delay0=10, repeat=0, howmuch=10000, reset=1, trig_delay=10):

        self['SEQ'].set_size(t)
        self['SEQ'].set_clk_divide(self.divide)
        self['SEQ'].set_repeat(repeat)
        self['SEQ'].set_en_ext_start(1)
        self['SEQ'].write(t)
        self.init_pulser(trig_delay=trig_delay)
        # self['SEQ'].start()
        s = "sel_col row:%d exp:%d delay0:%d repeat:%d howmuch:%d reset:%d divide:%d" % (
                row, exp, delay0, repeat, howmuch, reset, self.divide)
        self.l.append(s)


    def init_pulser(self, trig_delay=10, neg_edge=0):
        self["SW"]["NEG_EDGE"] = neg_edge
        self["SW"].write()
        
        self["PULSE_DELAY"].reset()
        self["PULSE_DELAY"].set_delay(trig_delay)
        self["PULSE_DELAY"].set_width(10)
        self["PULSE_DELAY"].set_repeat(1)


    def sel_one(self, col=25, row=12, exp=100, repeat=0, howmuch=11200, reset=1):
        if howmuch == -1:
            howmuch = exp * 10 + 20
        self['SEQ'].reset()
        self['SEQ'].clear()

        # # clear all shift registers
        t = 0
        # # select row
        for i in range(row):
            if i == 0:
                rst_en = 1
            else:
                rst_en = 0
            self['SEQ']['RST_EN_COL'][t] = 0
            self['SEQ']['CLK_COL'][t] = 0
            self['SEQ']['RST_EN_20'][t] = rst_en
            self['SEQ']['CLK_ROW_20'][t] = 0
            self['SEQ']['RST_ROW_20'][t] = 0
            self['SEQ']['RST2_20'][t] = 1
            self['SEQ']['RST1_20'][t] = 1
            self['SEQ']['RST2_40'][t] = 1
            self['SEQ']['RST1_40'][t] = 1
            self['SEQ']['RST_EN_40'][t] = rst_en
            self['SEQ']['CLK_ROW_40'][t] = 0
            self['SEQ']['RST_ROW_40'][t] = 0
            self['SEQ']['ADC_SYNC'][t] = 0
            
            t = t + 1
            self['SEQ']['RST_EN_COL'][t] = 0
            self['SEQ']['CLK_COL'][t] = 0
            self['SEQ']['RST_EN_20'][t] = rst_en
            self['SEQ']['CLK_ROW_20'][t] = 1
            self['SEQ']['RST_ROW_20'][t] = 0
            self['SEQ']['RST2_20'][t] = 1
            self['SEQ']['RST1_20'][t] = 1
            self['SEQ']['RST2_40'][t] = 1
            self['SEQ']['RST1_40'][t] = 1
            self['SEQ']['RST_EN_40'][t] = rst_en
            self['SEQ']['CLK_ROW_40'][t] = 1
            self['SEQ']['RST_ROW_40'][t] = 0
            self['SEQ']['ADC_SYNC'][t] = 0
            t = t + 1
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 0
        self['SEQ']['CLK_ROW_20'][t] = 0
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 1
        self['SEQ']['RST1_20'][t] = 1
        self['SEQ']['RST2_40'][t] = 1
        self['SEQ']['RST1_40'][t] = 1
        self['SEQ']['RST_EN_40'][t] = 0
        self['SEQ']['CLK_ROW_40'][t] = 0
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 0
        t = t + 1
        # select col
        for i in range(col):
            if i == 0:
                rst_en = 1
            else:
                rst_en = 0
            self['SEQ']['RST_EN_COL'][t] = rst_en
            self['SEQ']['CLK_COL'][t] = 0
            self['SEQ']['RST_EN_20'][t] = 0
            self['SEQ']['CLK_ROW_20'][t] = 0
            self['SEQ']['RST_ROW_20'][t] = 0
            self['SEQ']['RST2_20'][t] = 1
            self['SEQ']['RST1_20'][t] = 1
            self['SEQ']['RST2_40'][t] = 1
            self['SEQ']['RST1_40'][t] = 1
            self['SEQ']['RST_EN_40'][t] = 0
            self['SEQ']['CLK_ROW_40'][t] = 0
            self['SEQ']['RST_ROW_40'][t] = 0
            self['SEQ']['ADC_SYNC'][t] = 0
            t = t + 1
            self['SEQ']['RST_EN_COL'][t] = rst_en
            self['SEQ']['CLK_COL'][t] = 1
            self['SEQ']['RST_EN_20'][t] = 0
            self['SEQ']['CLK_ROW_20'][t] = 0
            self['SEQ']['RST_ROW_20'][t] = 0
            self['SEQ']['RST2_20'][t] = 1
            self['SEQ']['RST1_20'][t] = 1
            self['SEQ']['RST2_40'][t] = 1
            self['SEQ']['RST1_40'][t] = 1
            self['SEQ']['RST_EN_40'][t] = 0
            self['SEQ']['CLK_ROW_40'][t] = 0
            self['SEQ']['RST_ROW_40'][t] = 0
            self['SEQ']['ADC_SYNC'][t] = 0
            t = t + 1
     
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 0
        self['SEQ']['CLK_ROW_20'][t] = 0
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 1
        self['SEQ']['RST1_20'][t] = 1
        self['SEQ']['RST2_40'][t] = 1
        self['SEQ']['RST1_40'][t] = 1
        self['SEQ']['RST_EN_40'][t] = 0
        self['SEQ']['CLK_ROW_40'][t] = 0
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 0
        # # start repeat
#       ### read ADC here (before RESET)
        t = t + 1
        self['SEQ'].set_repeat_start(t)
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 0
        self['SEQ']['CLK_ROW_20'][t] = 0
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 1
        self['SEQ']['RST1_20'][t] = 1
        self['SEQ']['RST2_40'][t] = 1
        self['SEQ']['RST1_40'][t] = 1
        self['SEQ']['RST_EN_40'][t] = 0
        self['SEQ']['CLK_ROW_40'][t] = 0
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 1
        t = t + 1
        self['SEQ']['RST_EN_COL'][t:t + reset] = 0
        self['SEQ']['CLK_COL'][t:t + reset] = 0
        self['SEQ']['RST_EN_20'][t:t + reset] = 0
        self['SEQ']['CLK_ROW_20'][t:t + reset] = 0
        self['SEQ']['RST_ROW_20'][t:t + reset] = 1
        self['SEQ']['RST2_20'][t:t + reset] = 1
        self['SEQ']['RST1_20'][t:t + reset] = 1
        self['SEQ']['RST2_40'][t:t + reset] = 1
        self['SEQ']['RST1_40'][t:t + reset] = 1
        self['SEQ']['RST_EN_40'][t:t + reset] = 0
        self['SEQ']['CLK_ROW_40'][t:t + reset] = 0
        self['SEQ']['RST_ROW_40'][t:t + reset] = 1
        self['SEQ']['ADC_SYNC'][t:t + reset] = 0
        t = t + reset
        self['SEQ']['RST_EN_COL'][t] = 0
        self['SEQ']['CLK_COL'][t] = 0
        self['SEQ']['RST_EN_20'][t] = 0
        self['SEQ']['CLK_ROW_20'][t] = 0
        self['SEQ']['RST_ROW_20'][t] = 0
        self['SEQ']['RST2_20'][t] = 1
        self['SEQ']['RST1_20'][t] = 1
        self['SEQ']['RST2_40'][t] = 1
        self['SEQ']['RST1_40'][t] = 1
        self['SEQ']['RST_EN_40'][t] = 0
        self['SEQ']['CLK_ROW_40'][t] = 0
        self['SEQ']['RST_ROW_40'][t] = 0
        self['SEQ']['ADC_SYNC'][t] = 0
        self['SEQ'].set_wait(exp)
        self.init_adc(howmuch=howmuch)
        t = t + 1
        self['SEQ'].set_size(t)
        self['SEQ'].set_clk_divide(10)
        self['SEQ'].set_repeat(repeat)
        self['SEQ'].write(t)
        self['SEQ'].start()
        s = "sel_one row:%d col:%d exp:%d repeat:%d howmuch:%d reset:%d divide:%d" % (
                row, col, exp, repeat, howmuch, reset, self.divide)
        self.l.append(s)


    def init_adc(self, howmuch=10000):
        self['DATA_FIFO'].reset()
        self.howmuch = howmuch
        for ch in ['OUTA1', 'OUTA2']:
            self[ch].reset()
            self[ch].set_data_count(howmuch)
            self[ch].set_align_to_sync(True)

        
    def sel_all_get_adc(self, ext=True, timeout=1000):  # ## timeout[ms]
        if ext == True:
            self["PULSE_DELAY"].set_en(0)
        self['DATA_FIFO'].reset()
        for ch in ['OUTA1', 'OUTA2']:        
        # for ch in ['OUTA2']:
            self[ch].start()
        if ext == True:
            self["PULSE_DELAY"].set_en(1)
        else:
            self["PULSE_DELAY"].start()

        # self[ch].set_data_count(1000000)

        single = False
        nmdata = self['DATA_FIFO'].get_data()
        i = 0
        while not (self['OUTA1'].is_done() and self['OUTA2'].is_done()):
            nmdata = np.append(nmdata, self['DATA_FIFO'].get_data())
        # while not (self['OUTA1'].is_done()):
        #    nmdata = np.append(nmdata, self['DATA_FIFO'].get_data())
            if i > timeout:
                print "sel_all_get_adc() TIMEOUT"
                break
            else:
                time.sleep(0.001)
        nmdata = np.append(nmdata, self['DATA_FIFO'].get_data())

        # if(self.howmuch/2*2 != len(nmdata)):
            # print "Error: Data lost!", self.howmuch/2, len(nmdata)

        val1 = np.bitwise_and(nmdata, 0x00003fff)
        vals = np.right_shift(np.bitwise_and(nmdata, 0x10000000), 28)
        valc = np.right_shift(np.bitwise_and(nmdata, 0x60000000), 29)
       
        if(not single):
            val0 = np.right_shift(np.bitwise_and(nmdata, 0x0fffc000), 14)
            val1 = np.reshape(np.vstack((val0, val1)), -1, order='F')
            sync = np.reshape(np.vstack((vals, vals)), -1, order='F')
            valc = np.reshape(np.vstack((valc, valc)), -1, order='F')
        # return val1
        val = np.empty([2, len(val1) / 2], dtype=np.int32)
        for i in [0, 1]:
            val0 = val1[valc == i]
            if len(val[i, :]) == len(val0):
                val[i, :] = val1[valc == i]
            elif len(val[i, :]) < len(val0):
                val[i, :] = val1[valc == i][:len(val[i, :])]
                # print "WARN data size: all=",len(val1),"ch%d"%i,len(val[i,:]),"dat=",len(val0)
            else:
                val[i, :len(val0)] = val1[valc == i]
                val[i, len(val0):] = 0
                # print "WARN data size: all=",len(val1),"ch%d"%i,len(val[i,:]),"dat=",len(val0)
        return val


    def get_adc(self):
        self['DATA_FIFO'].reset()
        for ch in ['OUTA1', 'OUTA2']:        
        # for ch in ['OUTA2']:
            self[ch].start()

        # self[ch].set_data_count(1000000)

        single = False
        nmdata = self['DATA_FIFO'].get_data()
        i = 0

        while not (self['OUTA1'].is_done() and self['OUTA2'].is_done()):
            nmdata = np.append(nmdata, self['DATA_FIFO'].get_data())
        # while not (self['OUTA1'].is_done()):
        #    nmdata = np.append(nmdata, self['DATA_FIFO'].get_data())
            i = i + 1
            if i > 500:
                time.sleep(0.001) # was 0.001            

        nmdata = np.append(nmdata, self['DATA_FIFO'].get_data())

        # if(self.howmuch/2*2 != len(nmdata)):
            # print "Error: Data lost!", self.howmuch/2, len(nmdata)

        val1 = np.bitwise_and(nmdata, 0x00003fff)
        vals = np.right_shift(np.bitwise_and(nmdata, 0x10000000), 28)
        valc = np.right_shift(np.bitwise_and(nmdata, 0x60000000), 29)
       
        if(not single):
            val0 = np.right_shift(np.bitwise_and(nmdata, 0x0fffc000), 14)
            val1 = np.reshape(np.vstack((val0, val1)), -1, order='F')
            sync = np.reshape(np.vstack((vals, vals)), -1, order='F')
            valc = np.reshape(np.vstack((valc, valc)), -1, order='F')
        # return val1
        val = np.empty([2, len(val1) / 2], dtype=np.int32)
        for i in [0, 1]:
            val0 = val1[valc == i]
            if len(val[i, :]) == len(val0):
                val[i, :] = val1[valc == i]
            elif len(val[i, :]) < len(val0):
                val[i, :] = val1[valc == i][:len(val[i, :])]
                # print "WARN data size: all=",len(val1),"ch%d"%i,len(val[i,:]),"dat=",len(val0)
            else:
                val[i, :len(val0)] = val1[valc == i]
                val[i, len(val0):] = 0
                # print "WARN data size: all=",len(val1),"ch%d"%i,len(val[i,:]),"dat=",len(val0)
        return val


    def spectrum_raw(self, n=1000000, howmuch=10000):
        self.init_adc(howmuch=howmuch)
        chunk = 10000
        ii = n / chunk
        for i in range(ii):
            with open("dat%d.npy" % i, "wb") as f:
                for j in range(chunk):
                    np.save(f, self.get_adc())
        jj = n % chunk
        if jj != 0:
            with open("dat%d.npy" % i + 1, "wb") as f:
                np.save(f, t.get_adc())


    def img(self, n=10000):
        divide = 4
        col = 48
        row = 35
        exp = 100
        
        d = t.get_adc()
        diff = d[0, 1:55] - d[0, :54]
        row_begin = np.argmax(diff[0, :])
        baseline = d[:, row_begin + divide * 2 - 1:row_begin + (divide * 2 * (col + 1)) * row:divide * 2]
        data = d[:, row_begin + (divide * 2 * (col + 1)) * row + divide * (exp + 2) + divide * 2 - 1:(
                 row_begin + (divide * 2 * (col + 1)) * row * 2 + divide * (exp + 2)):8]
        return data - baseline


    def trigger(self, th, period, save=True):
        t1 = 1100
        t0 = 100
        flg = 0
        while flg == 0:
            dat = self.get_adc()
            for j in range(2):
                arglist = np.argwhere(dat[j, t1::period] < np.median(dat[j, :]) - th[j])
                if len(arglist) == 0:
                    continue
                flg = 1
                arglist = arglist[:, 0]
                with open("trigger%d.npy" % j, "ab") as f:
                    for i, a in enumerate(arglist):
                        np.save(f, dat[j, a * period + t0:(a + 1) * period + t0])
        self.l.append("trigger th:%d %d" % (th[0], th[1]))
        return dat
 
        
    def take_single_data(self, add_plot=True, show_info=True, sample_start=140, sample_period=1120, sample_sub_start=1000):
        samples = self.get_adc()
        
        sdata_a = samples[sample_sub_start::sample_period]
        sdata_ax = range(sample_sub_start, len(samples), sample_period)

        sdata_b = samples[sample_start::sample_period]
        sdata_bx = range(sample_start, len(samples), sample_period)
        
        size = min(len(sdata_a), len(sdata_b))  # just make the size same

        # diff = map(operator.sub, sdata_a[0:size], sdata_b[0:size])
        diff = sdata_a[0:size] - sdata_b[0:size]

        mean = np.mean(diff)
        stddev = np.std(diff)

        if show_info:
            # print 'row=', row, 'col=' , col, " stdev:", stddev, 'samples:', len(diff) ,'mean:', mean
            print 'row=', row, 'col=' , col, " stdev:", stddev, 'samples:', len(diff) , 'mean:', mean        
        if add_plot:
            plt.plot(samples)
            plt.plot(sdata_ax, sdata_a, 'ro')
            plt.plot(sdata_bx, sdata_b, 'go')
        
        return mean, stddev, diff
