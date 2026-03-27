# 🎙️ Litens Talk — MP3 Transcriber + Animated MP4 Generator

> **"This very episode was transcribed using our own project."** — Zeeshan, Litens Talk

Upload any MP3 podcast episode → get an AI transcription → export an animated MP4 with waveform visualization and synced subtitles.

### 🎙️ Litens
[![YouTube](https://img.shields.io/badge/YouTube-@Litends-FF0000?style=flat&logo=youtube)](https://youtube.com/@Litends)
[![Instagram](https://img.shields.io/badge/Instagram-@litendsco-E1306C?style=flat&logo=instagram)](https://instagram.com/litendsco)
[![Facebook](https://img.shields.io/badge/Facebook-Litends-1877F2?style=flat&logo=facebook)](https://facebook.com/profile.php?id=61576822259468)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-litends-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/company/litends)
[![Spotify](https://img.shields.io/badge/Spotify-Litens_Talk-1DB954?style=flat&logo=spotify)](https://open.spotify.com/show/7Gm4QCvLZI8qfnBoESAub4)
[![Website](https://img.shields.io/badge/Website-litends.com-lightgrey?style=flat&logo=google-chrome)](https://litends.com)

### 👤 Zeeshan (Builder)
[![Instagram](https://img.shields.io/badge/Instagram-@zeesejo-E1306C?style=flat&logo=instagram)](https://instagram.com/zeesejo)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-zeesejo-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/zeesejo)
[![YouTube](https://img.shields.io/badge/YouTube-ZeeseJones-FF0000?style=flat&logo=youtube)](https://youtube.com/c/ZeeseJones)

---

## ✨ Features
- 🤖 **Local Whisper transcription** — no API key, runs fully offline
- ⚡ **GPU accelerated** — CUDA for Whisper (fp16) + `h264_nvenc` for video encoding
- 🎬 **Animated MP4** — cyan glowing waveform, synced subtitles, progress bar, timestamp
- 📄 **SRT subtitle file** — download and use on any platform
- 🔤 **Custom vocab corrections** — fix proper nouns, brand names, names (`corrections.py`)
- 🌐 **Gradio web UI** — simple drag-and-drop interface

## 🚀 Setup

```bash
git clone https://github.com/Zeesejo/mp3-to-mp4-transcriber
cd mp3-to-mp4-transcriber
pip install -r requirements.txt
python app.py
```

**Prerequisites:**
- Python 3.9+
- `ffmpeg` + `ffprobe` on system PATH → [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
- NVIDIA GPU (optional but recommended) → install [PyTorch CUDA](https://pytorch.org/get-started/locally/)

## 🗂️ Project Structure

| File | Purpose |
|---|---|
| `app.py` | Gradio UI entry point |
| `transcriber.py` | Whisper transcription (GPU/CPU auto-detect) |
| `video_maker.py` | FFmpeg pipe renderer — waveform + subtitles |
| `corrections.py` | Post-processing word corrections dictionary |
| `requirements.txt` | Python dependencies |

## 🔤 Custom Corrections

Edit `corrections.py` to fix any words Whisper gets wrong:

```python
CORRECTIONS = {
    "zishan":  "Zeeshan",
    "littons": "Litens",
    # add your own...
}
```

## 📡 Litens Talk

*Litens Talk is a podcast about AI, building things from scratch, and the mindset it takes to actually make it.*

- ▶️ [YouTube @Litends](https://youtube.com/@Litends)
- 📸 [Instagram @litendsco](https://instagram.com/litendsco)
- 📘 [Facebook](https://facebook.com/profile.php?id=61576822259468)
- 💼 [LinkedIn](https://linkedin.com/company/litends)
- 🎵 [Spotify — Litens Talk](https://open.spotify.com/show/7Gm4QCvLZI8qfnBoESAub4)
- 🌐 [litends.com](https://litends.com)

---

Built with ❤️ by [Zeeshan](https://github.com/Zeesejo) · Powered by [OpenAI Whisper](https://github.com/openai/whisper) · [FFmpeg](https://ffmpeg.org) · [Gradio](https://gradio.app)
