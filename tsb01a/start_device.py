import tsb01

device = tsb01.tsb01(channels=['OUTA2'])
device.init()

device.sel_one(row=11, col=39, howmuch=100000, exp=100)
# device.sel_all(divide=12, howmuch=270000, repeat=0, reset=10, delay0=10, exp=50, size=(32, 12))