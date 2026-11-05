import sys, sherpa_onnx, soundfile as sf, numpy as np
D='../model/sherpa-onnx-supertonic-3-tts-int8-2026-05-11/'
def make():
    c=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(supertonic=sherpa_onnx.OfflineTtsSupertonicModelConfig(
      duration_predictor=D+'duration_predictor.int8.onnx',text_encoder=D+'text_encoder.int8.onnx',vector_estimator=D+'vector_estimator.int8.onnx',
      vocoder=D+'vocoder.int8.onnx',tts_json=D+'tts.json',unicode_indexer=D+'unicode_indexer.bin',voice_style=D+'voice.bin'),num_threads=4,provider='cpu'))
    return sherpa_onnx.OfflineTts(c)
def gen(tts,text,sid,speed=1.0,steps=16):
    g=sherpa_onnx.GenerationConfig(); g.sid=sid; g.num_steps=steps; g.speed=speed; g.extra["lang"]="ko"
    a=tts.generate(text,g); return np.array(a.samples,dtype=np.float32), a.sample_rate
def f0(x,sr):
    # crude autocorrelation pitch median on voiced frames
    fr=int(.04*sr); out=[]
    for i in range(0,len(x)-fr,fr):
        s=x[i:i+fr]; 
        if np.sqrt((s**2).mean())<0.02: continue
        s=s-s.mean(); ac=np.correlate(s,s,'full')[fr-1:]
        lo,hi=int(sr/400),int(sr/70); k=lo+np.argmax(ac[lo:hi]); out.append(sr/k)
    return np.median(out) if out else 0
if __name__=='__main__':
    tts=make()
    for sid in range(10):
        x,sr=gen(tts,"바닷가 작은 마을, 딸기 향으로 아침을 여는 가게.",sid)
        sf.write(f'v{sid}.wav',x,sr); print(sid,sr,round(len(x)/sr,2),'f0',round(f0(x,sr)))
