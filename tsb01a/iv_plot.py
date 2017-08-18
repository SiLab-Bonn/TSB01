# import numpy as np
# from matplotlib import pyplot as plt
# from matplotlib.backends.backend_pdf import PdfPages
# 
# data1 = np.loadtxt('/home/silab/Desktop/iv_curve_tsb01a_100um_pcb2.tsv', comments='#')
# data4 = np.loadtxt('/home/silab/Desktop/iv_curve_tsb01a_100um_pcb2_new.tsv', comments='#')
# data2 = np.loadtxt('/home/silab/Desktop/iv_curve_tsb01a_100um.tsv', comments='#')
# data3 = np.loadtxt('/home/silab/Desktop/iv_curve_tsb01a_300um.tsv', comments='#')
# 
# labels = ['100um_new_pcb', '100um_new_pcb_2', '100um_old_pcb', '300um_old_pcb']
# 
# pdf = PdfPages('/home/silab/Desktop/iv_curves.pdf')
# 
# for index, data in enumerate([data1, data4, data2, data3]):
#     voltage = data[:,0]
#     current = data[:,1]
#     
#     fig = plt.figure()
#     ax1 = plt.subplot(211)
#     ax1.set_title(labels[index])
#     ax2 = plt.subplot(212, sharex=ax1)
#     ax1.plot(-1 * voltage, -1 * current, '.-')
#     ax2.plot(-1 * voltage, -1 * current, '.-')
#     ax1.set_yscale('log')
#     # ax1.grid()
#     # ax2.grid()
#     # ax2.set_yscale('')
#     ax1.set_ylabel('I / nA')
#     ax2.set_ylabel('I / nA')
#     
#     ax2.set_xlabel('U / V')
#     pdf.savefig(fig)
#     
# pdf.close()

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

data1 = np.loadtxt('/home/silab/Desktop/iv_curve_tsb01a_100um_pcb2.tsv', comments='#')
data4 = np.loadtxt('/home/silab/Desktop/iv_curve_tsb01a_100um_pcb2_new.tsv', comments='#')
data2 = np.loadtxt('/home/silab/Desktop/iv_curve_tsb01a_100um.tsv', comments='#')
data3 = np.loadtxt('/home/silab/Desktop/iv_curve_tsb01a_300um.tsv', comments='#')

labels = ['100um_new_pcb', '100um_new_pcb_2', '100um_old_pcb', '300um_old_pcb']

pdf = PdfPages('/home/silab/Desktop/iv_curves.pdf')

voltage_2 = data2[:,0]
current_2 = data2[:,1]

voltage_3 = data3[:,0]
current_3 = data3[:,1]

fig = plt.figure()
ax1 = plt.subplot(111)
# ax2 = plt.subplot(212, sharex=ax1)

ax1.set_title('')
ax1.plot(-1 * voltage_2, -1 * current_2, '.-', label='thinned to 100um')
ax1.plot(-1 * voltage_3, -1 * current_3, '.-', label='w/o backside processing')
ax1.legend()
ax1.set_yscale('log')
ax1.grid()
# ax2.grid()
# ax2.set_yscale('log')
ax1.set_ylabel('I / nA')
# ax2.set_ylabel('I / nA')
ax1.set_xlabel('U / V')
plt.show()
    
