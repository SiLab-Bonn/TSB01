
import time
import numpy as np
import matplotlib.pyplot as plt
import tables
from numba import njit

@njit
def _analyse_adc(raw):
    res_i=0
    res=np.empty(len(raw)*2,dtype=np.int16)
    for raw_i in range(len(raw)):
        if raw[raw_i] & 0xE0000000 == 0x20000000:
            res[res_i] = raw[raw_i] & 0x00003fff
            res[res_i+1] = (raw[raw_i] &0x0fffc000) >> 14
            res_i=res_i+2
    return res[:res_i]

@njit
def _mk_img(raw_array,res,col_n=31,row_n=12,div=12):
    r1_off=div*3+6
    r1_len=div*2*col_n
    r0_off=r1_off+r1_len+23*div ## TODO get 23 from reset and delay
    
    r_off=div
    r_len=r0_off+r1_len+6
    
    f_off=0
    f_len=1866*div ##TODO calc from col_n,row_n,reset,delay,exposure...
    
    dat=np.empty(len(raw_array[0,:])*2,dtype=np.int16)
    res_i=0
    for raw_i in range(len(raw_array)):
        ### convert raw to adc data
        dat_i=0
        for r in raw_array[raw_i,:]:
            if r & 0xE0000000 == 0x20000000:
                dat[dat_i] = r & 0x00003fff
                dat[dat_i+1] = (r &0x0fffc000) >> 14
                dat_i=dat_i+2

        ### get valid data (baseline and signal) 
        f_n=len(dat)/f_len
        for i in range(f_n):
            f_dat=dat[f_off+i*f_len:f_off+(i+1)*f_len]
            for j in range(row_n):
                r_dat=f_dat[r_off+j*r_len:r_off+(j+1)*r_len]
                r1_dat=r_dat[r1_off:r1_off+r1_len]
                r0_dat=r_dat[r0_off:r0_off+r1_len]
                for k in range(col_n):
                    if i!=f_n-1:
                        res[res_i+i]["bl"][k,j]=np.median(r0_dat[k*div*2:(k+1)*div*2][2:-1])
                    if i!=0:
                        res[res_i+i-1]["sig"][k,j]=np.median(r1_dat[k*div*2:(k+1)*div*2][2:-1])
        res_i=res_i+i
    return res[:res_i]

def tsb01_interpreter(fin,fout,col_n,row_n,div): 
    f_n=12 ### TODO make a better guess according to col_n,row_n,..etc 
    f_nn=f_n-1
    n=1000

    hit_dtype=np.dtype([("bl","f8",(col_n,row_n)),("sig","f8",(col_n,row_n))])
    hit=np.empty(f_nn*n,dtype=hit_dtype)

    with tables.open_file(fout,"w") as f_o:
        description=np.zeros((1,),dtype=hit_dtype).dtype
        hit_table=f_o.create_table(f_o.root,name="Hits",description=description,title='hit_data')
        with tables.open_file(fin) as f:
            end=len(f.root.event_data)
            print "data length",end
            start=0
            t0=time.time()
            while start<end:
                tmpend=min(start+n,end)
                raw_array=f.root.event_data[start:tmpend]
                hit=_mk_img(raw_array,hit,col_n,row_n,div)
                hit_table.append(hit)
                hit_table.flush()
                print time.time()-t0,start,"%.2f%%"%(100.0*tmpend/end)
                start=tmpend

if __name__== "__main__":
    import sys
    fin=sys.argv[1]
    fout=fin[:-3]+"inter2.h5"
    tsb01_interpreter(fin,fout,col_n=31,row_n=12, div=12)
    print fout

