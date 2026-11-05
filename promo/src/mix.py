import numpy as np, soundfile as sf
from script import LINES
SR=44100; N=int(38.0*SR)
m,sr=sf.read('music.wav'); assert sr==SR
v=np.zeros(N)
for i,(t,_,_) in enumerate(LINES):
    x,sr=sf.read(f's2_{i}.wav'); assert sr==SR
    x=x/np.abs(x).max()*0.9
    a=int(t*SR); v[a:a+len(x)]+=x[:N-a]
# ducking envelope from voice
env=np.abs(v); w=int(0.05*SR)
env=np.convolve(env,np.ones(w)/w,'same')
on=(env>0.01).astype(float)
# hold + smooth (attack ~0.15s, release ~0.5s)
k=int(0.35*SR); on=np.convolve(on,np.ones(k)/k,'same')>0
g=np.where(on,0.26,0.75).astype(float)
s=int(0.25*SR); g=np.convolve(np.pad(g,(s,s),'edge'),np.ones(2*s)/(2*s),'same')[s:-s][:N]
mix=m*g[:,None]+np.stack([v,v],1)*0.95
sf.write('voice.wav',v.astype(np.float32),SR)
sf.write('mix_raw.wav',(mix/np.abs(mix).max()*0.9).astype(np.float32),SR)
print('ok')
