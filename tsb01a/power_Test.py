import tsb01
import numpy as np
from matplotlib import pyplot as plt
import time

device = tsb01.tsb01()
device.init()

device.sel_all(divide=12, howmuch=5000, repeat=0, exp=10)
print device['OUTA1'].is_done(), device['OUTA2'].is_done()
time.sleep(.1)

raw_data = device.get_adc()

if np.any(raw_data == None):
    device.stop_adc()
    device.init_adc(howmuch=5000)
    print device['OUTA1'].is_done(), device['OUTA2'].is_done()

def analyze_nmdata(nmdata):
        single = False
        
        val1 = np.bitwise_and(nmdata, 0x00003fff)
        vals = np.right_shift(np.bitwise_and(nmdata, 0x10000000), 28)
        valc = np.right_shift(np.bitwise_and(nmdata, 0x60000000), 29)
       
        if(not single):
            val0 = np.right_shift(np.bitwise_and(nmdata, 0x0fffc000), 14)
            val1 = np.reshape(np.vstack((val0, val1)), -1, order='F')
            # unused variable sync
#             sync = np.reshape(np.vstack((vals, vals)), -1, order='F')
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

data = analyze_nmdata(raw_data)[1]

x = np.arange(0, 5000)
# plt.plot(x, data, 'b-')
plt.plot(x, data, 'b-')
plt.plot(x[::6], data[::6], 'ro')
plt.show()

# device['FADC_VREF'].set_voltage(0.88, unit='V')
# device['RST_VOL'].set_voltage(0.8, unit='V')
# device.get_adc()

# start_time = timeit.default_timer()
# 
# while True:
#     data = device.get_adc()[0]
# 
#     if data[0] < 8880:
#         elapsed = timeit.default_timer() - start_time
# 
#         print elapsed
#         plt.plot(data)
#         plt.show()
#         
#         start_time = timeit.default_timer()
