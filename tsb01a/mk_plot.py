
import matplotlib
w=1.4
h=1.4
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
    print "total frame",len(img),"col-row",np.shape(img[0]["sig"])

    plt.subplot(221)
    frame=len(img)/2
    plt.pcolor(img["bl"][frame,:,:]-img["sig"][frame,:,:])
    plt.title("Image of frame%d"%frame)
    plt.colorbar()
    plt.xlabel("Column [pix]")
    plt.ylabel("Row [pix]")
    plt.xlim(0,img[frame]["sig"].shape[1])
    plt.ylim(0,img[frame]["sig"].shape[0])

    plt.subplot(222)
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
    bins=np.arange(-10,60)
    plt.subplot(223)
    plt.hist(hit[:,col,row],bins=bins,histtype="step");
    #plt.ylim(0,len(img)/100)
    plt.yscale("log")
    plt.title("1 Pixel=(%d,%d)"%(col,row))
    plt.xlabel("Signal [ADC]")
    plt.ylabel("#")

    plt.subplot(224)
    single=hit[:,col,row][np.bitwise_and(
                   np.bitwise_and(
                   np.bitwise_and(hit[:,col+1,row]<th,hit[:,col-1,row]<th),
                   np.bitwise_and(hit[:,col,row+1]<th,hit[:,col,row-1]<th)),
                   np.bitwise_and(
                   np.bitwise_and(hit[:,col-1,row+1]<th,hit[:,col+1,row+1]<th),
                   np.bitwise_and(hit[:,col-1,row-1]<th,hit[:,col+1,row-1]<th)))]
    hist=plt.hist(single,bins=bins,histtype="step") 
    plt.title("Single pixel cluster=(%d,%d)"%(col,row))
    #plt.title("Pixel=(%d,%d)"%(col,row))
    plt.xlabel("Signal [ADC]")
    plt.ylabel("#")
    plt.ylim(0,np.max(hist[0][hist[1][:-1]>=th])*2)
    plt.tight_layout()
    plt.savefig(fout)

if __name__=="__main__":
    import sys
    if len(sys.argv)<4:
        print "mk_plot.py <fin> <col> <row> [th]"
        sys.exit()
    elif len(sys.argv)==5:
        th=int(sys.argv[4])
    fin=sys.argv[1]
    col=int(sys.argv[2])
    row=int(sys.argv[3])
    fout=fin[:-3]+"%d-%d.png"%(col,row)
    mk_plot(fin,fout,col,row)
    print fout
