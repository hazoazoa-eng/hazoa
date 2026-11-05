from script import LINES
def ts(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60
    return f"{h}:{m:02d}:{s:05.2f}"
head="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Pretendard ExtraBold,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,2,5,0,0,0,1
Style: Band,Pretendard ExtraBold,10,&H38181818,&H38181818,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]
for i,(t,txt,sub) in enumerate(LINES):
    if not sub: continue
    scene=int(t//4)*4
    a=scene+0.2; b=scene+3.85
    ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Band,,0,0,0,,{{\\fad(180,180)\\pos(0,0)\\p1}}m 0 1500 l 1080 1500 l 1080 1800 l 0 1800{{\\p0}}")
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Sub,,0,0,0,,{{\\fad(180,180)\\pos(540,1600)}}{sub[0]}")
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Sub,,0,0,0,,{{\\fad(180,180)\\pos(540,1700)}}{sub[1]}")
open('subs.ass','w',encoding='utf-8').write(head+"\n".join(ev)+"\n")
# also an SRT of the full narration (for Instagram captions / editing)
srt=[]
import soundfile as sf
for i,(t,txt,_) in enumerate(LINES):
    d=sf.info(f's2_{i}.wav').duration
    def st(x): return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int(round(x%1*1000)):03d}"
    srt.append(f"{i+1}\n{st(t)} --> {st(t+d+0.2)}\n{txt}\n")
open('narration.srt','w',encoding='utf-8').write("\n".join(srt))
