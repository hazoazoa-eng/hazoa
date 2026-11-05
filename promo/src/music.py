import numpy as np, soundfile as sf
SR=44100; DUR=38.0; N=int(SR*DUR)
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
E=0.25  # eighth note = 0.25s (120bpm), bar = 2s
def hz(m): return 440*2**((m-69)/12)
def add(sig,t,gain=1.0,pan=0.0):
    i=max(int(t*SR),0); j=min(i+len(sig),N)
    if i>=N: return
    s=sig[:j-i]*gain
    L[i:j]+=s*np.sqrt((1-pan)/2); R[i:j]+=s*np.sqrt((1+pan)/2)
def piano(m,dur=1.6,bright=1.0):
    f=hz(m); n=int(dur*SR); t=np.arange(n)/SR
    s=np.zeros(n)
    for k,a in [(1,1.0),(2,.45*bright),(3,.18*bright),(4,.09*bright),(5,.04*bright)]:
        fk=f*k*np.sqrt(1+0.0004*k*k)
        s+=a*np.sin(2*np.pi*fk*t+rng.random()*6)*np.exp(-t*(1.6+k*1.1)*(f/260)**.35)
    att=np.minimum(t/0.006,1); rel=np.minimum((dur-t)/0.08,1)
    return s*att*rel*0.22
def glock(m,dur=1.4):
    f=hz(m); n=int(dur*SR); t=np.arange(n)/SR
    s=np.sin(2*np.pi*f*t)*np.exp(-t*2.6)+.35*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*7)+.12*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*14)
    return s*np.minimum(t/0.002,1)*np.minimum((dur-t)/0.05,1)*0.16
def pad(ms,dur,att=0.8,rel=0.9,dark=1.0):
    n=int(dur*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for m in ms:
        for det in (-0.07,0.0,0.07):
            f=hz(m+det)
            for k in range(1,6):
                s+=np.sin(2*np.pi*f*k*t+rng.random()*6)/(k**(1.6*dark))
    env=np.minimum(t/att,1)*np.minimum(np.maximum(dur-t,0)/rel,1)
    trem=1+0.06*np.sin(2*np.pi*0.25*t)
    return s*env*trem*0.012
def bass(m,dur):
    f=hz(m); n=int(dur*SR); t=np.arange(n)/SR
    s=np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2*f*t)*np.exp(-t*3)
    return s*np.minimum(t/0.01,1)*np.exp(-t*0.7)*np.minimum((dur-t)/0.1,1)*0.18
def shaker(acc):
    n=int(0.09*SR); t=np.arange(n)/SR; x=rng.standard_normal(n)
    x=np.diff(np.concatenate([[0],x]))  # crude highpass
    return x*np.exp(-t*45)*np.minimum(t/0.004,1)*(0.035 if acc else 0.02)
def kick():
    n=int(0.35*SR); t=np.arange(n)/SR
    f=48+70*np.exp(-t*30); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*9)*0.32
def swell(dur):
    n=int(dur*SR); t=np.arange(n)/SR; x=rng.standard_normal(n)
    x=np.convolve(x,np.ones(6)/6,'same')
    return x*(t/dur)**3*0.05
# chords: name -> (bass, arp8, pad)
C={'F':(41,[53,60,65,69,72,69,65,60],[57,60,65,69]),
   'C/E':(40,[52,55,60,64,67,64,60,55],[55,60,64,67]),
   'Dm':(38,[50,57,62,65,69,65,62,57],[57,62,65,69]),
   'Bb':(34,[46,53,58,62,65,62,58,53],[58,62,65,70]),
   'C':(36,[48,55,60,64,67,64,60,55],[55,60,64,67]),
   'Bbmaj7':(34,[46,53,57,62,65,62,57,53],[57,62,65,69]),
   'Am':(33,[45,52,57,60,64,60,57,52],[57,60,64,69]),
   'Gm7':(31,[43,50,53,58,62,58,53,50],[53,58,62,65]),
   'Csus4':(36,[48,55,60,65,67,65,60,55],[55,60,65,67]),
   'Fadd9':(41,[53,60,65,67,69,72,77,72],[57,60,65,67])}
BARS=['F','C/E','Dm','Bb','F','C','Bb','C', 'Dm','Bbmaj7', 'Bb','C','Am','Dm', 'Bbmaj7','Gm7','Csus4','Bbmaj7','Fadd9']
# section per bar: intro, verse, night, full, quiet, end
SEC=['intro']*2+['verse']*6+['night']*2+['full']*4+['quiet']*4+['end']
MEL={2:[(0,81,2),(2,86,2),(4,84,2),(6,81,2)],3:[(0,77,3),(3,79,1),(4,81,4)],
     4:[(0,84,2),(2,81,2),(4,77,2),(6,81,2)],5:[(0,79,4),(4,76,2),(6,79,2)],
     6:[(0,86,2),(2,84,2),(4,82,2),(6,81,2)],7:[(0,79,6)],
     9:[(4,81,4)],
     10:[(0,86,2),(2,89,2),(4,86,2),(6,84,2)],11:[(0,79,2),(2,84,2),(4,88,4)],
     12:[(0,88,2),(2,84,2),(4,81,2),(6,84,2)],13:[(0,86,4),(4,81,4)],
     15:[(0,82,4)],16:[(4,79,4)],17:[(0,81,2),(2,84,2),(4,86,4)],18:[(0,89,8)]}
for b,name in enumerate(BARS):
    t0=b*2.0; sec=SEC[b]; bs,arp,pd=C[name]
    # pad
    padg={'intro':0.8,'verse':1.0,'night':1.3,'full':1.0,'quiet':1.2,'end':1.2}[sec]
    pdur=4.5 if sec=='end' else 2.45
    add(pad(pd,pdur,att=0.9 if b==0 else 0.35,dark=1.3 if sec in('night','quiet') else 1.0),t0,padg)
    # piano arpeggio
    if sec in ('intro','verse','full'):
        for k,m in enumerate(arp):
            g=(0.75 if sec=='intro' else 0.9)*(1.15 if k%4==0 else 0.85)
            add(piano(m,1.5),t0+k*E+rng.normal(0,0.004),g,pan=-0.25)
    elif sec in ('night','quiet'):
        for k in (0,2,4,6):
            add(piano(arp[k],2.0,bright=0.6),t0+k*E,0.8,pan=-0.2)
    else:  # end: rolled chord ringing
        for k,m in enumerate([41,53,60,65,67,69,72]):
            add(piano(m,4.0,bright=0.8),t0+k*0.06,0.9,pan=-0.15)
    # bass
    if sec in ('verse','full'): add(bass(bs,2.0),t0,1.0)
    if sec in ('night','quiet'): add(bass(bs,2.0),t0,0.6)
    if sec=='end': add(bass(bs,4.0),t0,0.8)
    # drums
    if (sec=='verse' and b>=4) or sec=='full':
        for k in range(8): add(shaker(k%2==1),t0+k*E+rng.normal(0,0.003),1.0,pan=0.35)
        add(kick(),t0,1.0); add(kick(),t0+4*E,0.8)
    # melody
    for (p,m,l) in MEL.get(b,[]):
        add(glock(m,max(l*E+0.6,1.0)),t0+p*E,1.0 if sec in('verse','full') else 0.8,pan=0.3)
add(swell(1.8),18.2,1.0)   # whoosh into the bright winter section
add(swell(1.2),26.8,0.6)   # into the question section
# simple stereo reverb by FFT convolution
def ir(seed):
    r=np.random.default_rng(seed); n=int(2.2*SR); t=np.arange(n)/SR
    x=r.standard_normal(n)*np.exp(-t*3.0); x=np.convolve(x,np.ones(8)/8,'same'); x[:int(.02*SR)]=0
    return x/np.sqrt((x**2).sum())
def conv(a,h):
    n=len(a)+len(h); nf=1<<int(np.ceil(np.log2(n)))
    return np.fft.irfft(np.fft.rfft(a,nf)*np.fft.rfft(h,nf),nf)[:len(a)]
wl=conv(L,ir(1)); wr=conv(R,ir(2))
L2=L+0.35*wl; R2=R+0.35*wr
# fade in/out
t=np.arange(N)/SR
env=np.minimum(t/0.4,1)*np.clip((DUR-t)/2.0,0,1)
out=np.stack([L2*env,R2*env],1)
out=out/np.abs(out).max()*0.89
sf.write('music.wav',out.astype(np.float32),SR)
print('ok',out.shape)
