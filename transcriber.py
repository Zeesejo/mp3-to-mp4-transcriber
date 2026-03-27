import whisper
import os

def transcribe_audio(mp3_path: str):
    """
    Transcribe an MP3 file using OpenAI Whisper.
    Returns: (segments list, path to .srt file)
    """
    model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
    result = model.transcribe(mp3_path)

    segments = result["segments"]  # [{start, end, text}, ...]
    srt_path = mp3_path.replace(".mp3", ".srt")
    _write_srt(segments, srt_path)

    return segments, srt_path


def _write_srt(segments, srt_path):
    """Write Whisper segments to an SRT subtitle file."""
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = _format_time(seg["start"])
            end = _format_time(seg["end"])
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")


def _format_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format."""
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
