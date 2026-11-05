import sherpa_onnx, soundfile as sf, glob, numpy as np
D='../asr/sherpa-onnx-zipformer-korean-2024-06-24/'
r=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=D+'encoder-epoch-99-avg-1.onnx',decoder=D+'decoder-epoch-99-avg-1.onnx',joiner=D+'joiner-epoch-99-avg-1.onnx',tokens=D+'tokens.txt',num_threads=4)
import sys
for f in sorted(glob.glob(sys.argv[1] if len(sys.argv)>1 else 'n?.wav')):
    x,sr=sf.read(f,dtype='float32')
    s=r.create_stream(); x=np.concatenate([np.zeros(int(.3*sr),np.float32),x,np.zeros(int(.8*sr),np.float32)]); s.accept_waveform(sr,x); r.decode_stream(s); print(f, s.result.text)
