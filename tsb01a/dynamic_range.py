import tsb01
import numpy as np
from time import sleep
from matplotlib import pyplot as plt

device = tsb01.tsb01()
device.init()
 
# device.sel_one(row=10, col=25, howmuch=100)
device.init_adc(howmuch=100)
means = np.empty(shape=1)
 
steps = 0.1
 
for voltage in np.arange(0, 1.8, 0.025):
    device['RST_VOL'].set_voltage(voltage, unit='V')
    data = device.get_adc()[0]
    print data
    mean = np.mean(data)
    means = np.append(means, mean)
       
#     sleep(0.1)
 
# for adc_ref in np.arange(0, 1.8, steps):
#     device.power(FADC_VREF=adc_ref)
#     data= device.get_adc()[0]
#     mean = np.mean(data)
#     means = np.append(means, mean)
#       
#     sleep(0.1)
 
plt.plot(np.arange(0, 1.8, steps), means[1:])
plt.xlabel('FADC_VREF / V')
plt.ylabel('ADC Baseline')
print means[1:]
plt.show()
