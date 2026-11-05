import sys, soundfile as sf, numpy as np
from st import make, gen
from script import LINES
sid=int(sys.argv[1]); tts=make()
# max length per slot: next line start - this start - 0.25 gap, capped at 3.6s for 4s scenes
for i,(t,txt,_) in enumerate(LINES):
    nxt = LINES[i+1][0] if i+1<len(LINES) else 37.6
    lim=min(nxt-t-0.3, 3.6 if i<7 else 4.2)
    sp=1.0
    for _ in range(6):
        x,sr=gen(tts,txt,sid,sp)
        # trim leading/trailing silence
        nz=np.where(np.abs(x)>0.01)[0]; x=x[max(nz[0]-int(.03*sr),0):nz[-1]+int(.12*sr)]
        d=len(x)/sr
        if d<=lim: break
        sp=round(sp*d/lim*1.02,3)
    sf.write(f's{sid}_{i}.wav',x,sr); print(i,'speed',sp,'dur',round(d,2),'lim',round(lim,2))
