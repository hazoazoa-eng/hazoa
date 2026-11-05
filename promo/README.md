# 인스타 홍보 맛보기 영상 — 백업

| 파일 | 내용 |
|---|---|
| `insta_teaser_final.mp4` | 완성본 (1080×1920, 38초, H.264/AAC, -14 LUFS) |
| `source/original_2026_11_06_01_10.mp4` | 원본 영상 (소리 없음) |
| `stems/bgm.flac` | 배경음악만 (직접 합성한 곡, 저작권 없음) |
| `stems/narration_full.flac` | 나레이션만 (영상 시간에 맞춰 배치됨) |
| `stems/line_0~8.flac` | 나레이션 문장별 음성 |
| `stems/final_mix.flac` | 음악 + 나레이션 최종 믹스 |
| `narration.srt` | 나레이션 대본 + 시간 |
| `subs.ass` | 화면에 박힌 자막 원본 |
| `src/` | 다시 만들 때 쓰는 스크립트와 폰트 (Pretendard ExtraBold, OFL) |

## 다시 만들기 (문구·목소리 수정 시)

모델 파일은 용량이 커서 저장소에 넣지 않았습니다. `src/`와 같은 높이에 `model/`, `asr/` 폴더를 두고 받으세요.

```bash
pip install "sherpa-onnx>=2" soundfile numpy
# 음성 모델 (Supertonic 3, 한국어 지원)
mkdir -p model && curl -sSL https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2 | tar xj -C model
# (선택) 발음 확인용 한국어 음성 인식 모델
mkdir -p asr && curl -sSL https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-zipformer-korean-2024-06-24.tar.bz2 | tar xj -C asr

cd src
# 1) script.py 에서 나레이션/자막 문구 수정
python3 gen_all.py 2      # 문장별 음성 생성 (2 = 사용한 여성 목소리, 0~5 여성 / 6~9 남성)
python3 music.py          # 배경음악 생성 → music.wav
python3 mix.py            # 나레이션 배치 + 음악 볼륨 자동 낮춤 → mix_raw.wav
python3 subs.py           # 자막 → subs.ass, narration.srt
# 2) 소리 크기 맞추고 영상 합치기
ffmpeg -y -i mix_raw.wav -af "highpass=f=38,equalizer=f=70:t=q:w=1:g=-3,loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 final_audio.wav
ffmpeg -y -i ../source/original_2026_11_06_01_10.mp4 -i final_audio.wav -map 0:v -map 1:a \
  -vf "subtitles=subs.ass:fontsdir=fonts,format=yuv420p" -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k -shortest -movflags +faststart insta_teaser_final.mp4
```
