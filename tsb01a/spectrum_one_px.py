import tsb01
from matplotlib import pyplot as plt
import numpy as np
import time
import progressbar

# Define how many amplitudes to take
n_samples = 500

# initialize FPGA
device = tsb01.tsb01()
device.init()

device.sel_one(row=10, col=22, howmuch=100)
amplitudes = np.zeros(shape=1)

pbar = progressbar.ProgressBar(widgets=['', progressbar.Percentage(), ' ', progressbar.Bar(marker='#', left='|', right='|'), ' ', progressbar.AdaptiveETA()], maxval=n_samples, poll=10, term_width=80).start()

# take n_samples amplitudes
for t in range(n_samples):
    data = device.get_adc()[0]
 
    first_mean = np.mean(data[0:12])
    last_mean = np.mean(data[30:45])
    
    amplitude = last_mean - first_mean
    amplitudes = np.append(amplitudes, amplitude)
    time.sleep(0.01)
    
    if t % 10 == 0:
        pbar.update(t)

pbar.finish()

fig = plt.figure()
ax = fig.add_subplot(111)
plt.hist(amplitudes, bins=50)
# write n_samples in plot
# plt.text(0.9, 0.9, '%s' %n_samples, horizontalalignment='right', verticalalignment='top', transform=ax.transAxes)
plt.xlabel('Amplitude / ADC units')
plt.ylabel('Counts')
plt.show()
