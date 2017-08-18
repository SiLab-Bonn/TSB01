'''
Connect VSRC0 (=RST_VOL) with A side of ADC connector (without white background)
'''

import tsb01
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

device = tsb01.tsb01()
device.init()

adc_channel = 1

device.sel_one()

def init_adc(howmuch=100):
    device['DATA_FIFO'].reset()
    for ch in ['OUTA1', 'OUTA2']:
        device[ch].reset()
        device[ch].set_data_count(howmuch)
        device[ch].set_align_to_sync(True)
 
init_adc(howmuch=100)

with PdfPages('source_voltage_sweeps.pdf') as pdf:
    means = np.empty(shape=1)
    for voltage in np.arange(0, 1.8, 0.1):
        device['RST_VOL'].set_voltage(voltage, unit='V')
        data = device.get_adc()[adc_channel]
        mean = np.mean(data)
        means = np.append(means, mean)
    
    plt.plot(np.arange(0, 1.8, 0.1), means[1:])
    plt.xlabel('RST_VOL / V')
    plt.ylabel('ADC Baseline')
    pdf.savefig()
    plt.close()

    # create new empty array for results and set all voltages back to default
    means = np.empty(shape=1)
    device.power()
    
    for voltage in np.arange(0, 1.8, 0.1):
        device['FADC_VREF'].set_voltage(voltage, unit='V')
        data = device.get_adc()[adc_channel]
        mean = np.mean(data)
        means = np.append(means, mean)
    
    plt.plot(np.arange(0, 1.8, 0.1), means[1:])
    plt.xlabel('FADC_VREF / V')
    plt.ylabel('ADC Baseline')
    pdf.savefig()
    plt.close()
