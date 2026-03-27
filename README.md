# 🎙️ MP3 → Transcription → Animated MP4

Upload an MP3 file, get it transcribed using OpenAI Whisper, and export an animated MP4 with scrolling subtitles and an audio waveform visualization.

## Features
- 🎤 Transcription via OpenAI Whisper (local, no API key needed)
- 🎬 Animated MP4 with waveform + scrolling subtitles
- 🌐 Simple Gradio web UI
- 💾 Downloadable `.srt` subtitle file

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## Requirements
- Python 3.9+
- `ffmpeg` installed and on PATH

## Usage
1. Open the Gradio UI in your browser
2. Upload any `.mp3` file
3. Wait for transcription + video rendering
4. Download your animated `.mp4`
