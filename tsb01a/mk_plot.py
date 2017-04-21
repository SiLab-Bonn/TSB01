
import matplotlib
w=1.4
h=0.7
pltsize=2
matplotlib.rcParams["font.size"]=7*pltsize
matplotlib.rcParams["legend.fontsize"]="small"
matplotlib.rcParams['figure.figsize']=4*pltsize*w,3*pltsize*h
matplotlib.rcParams["axes.color_cycle"]=["r","b","g","m","c","y","k","w"]

import numpy as np
import matplotlib.pyplot as plt
import tables

def mk_plot(fin,fout,col,row):
    with tables.open_file(fin) as f:
        img=f.root.Hits[:]
    print len(img)
    plt.subplot(121)
    binmax=max(np.max(img["bl"][:,col,row]),np.max(img["sig"][:,col,row]))
    binmin=min(np.min(img["bl"][:,col,row]),np.min(img["sig"][:,col,row]))
    print binmin,np.min(img["bl"][:,col,row]),np.min(img["sig"][:,col,row])
    bins=np.arange(binmin,binmax,1)

    hist0=plt.hist(img["bl"][:,col,row],bins=bins,histtype="step",label="reset");
    hist1=plt.hist(img["sig"][:,col,row],bins=bins,histtype="step",label="exposed");
    plt.yscale("log")
    plt.title("Raw data:col=%d row=%d"%(col,row))
    plt.legend(loc=[0.02,0.8])
    plt.xlabel("ADC value [ADC]")
    plt.ylabel("#")
    plt.ylim(0.5,1.1*max(np.max(hist0[0]),np.max(hist1[0])))

    hit=img["bl"]-img["sig"]
    plt.subplot(122)
    plt.hist(hit[:,col,row],bins=np.arange(-10,30),histtype="step");
    #plt.ylim(0,len(img)/100)
    plt.yscale("log")
    plt.title("Pixel=(%d,%d)"%(col,row))
    plt.xlabel("Signal [ADC]")
    plt.ylabel("#")

    plt.tight_layout()
    plt.savefig(fout)

if __name__=="__main__":
    import sys
    if len(sys.argv)!=4:
        print "mk_plot.py <fin> <col> <row>"
    fin=sys.argv[1]
    col=int(sys.argv[2])
    row=int(sys.argv[3])
    fout=fin[:-3]+"%d-%d.png"%(col,row)
    mk_plot(fin,fout,col,row)
    print fout
