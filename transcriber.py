import whisper
import os

def transcribe_audio(mp3_path: str, model_size: str = "base"):
    """
    Transcribe an MP3 using OpenAI Whisper.
    Returns: (segments list, path to .srt file)
    model_size options: tiny, base, small, medium, large
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(mp3_path, verbose=False)
    segments = result["segments"]

    srt_path = os.path.splitext(mp3_path)[0] + ".srt"
    _write_srt(segments, srt_path)

    return segments, srt_path


def _write_srt(segments, srt_path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = _fmt(seg["start"])
            end   = _fmt(seg["end"])
            text  = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")


def _fmt(seconds: float) -> str:
    ms = int(round((seconds % 1) * 1000))
    s  = int(seconds) % 60
    m  = int(seconds // 60) % 60
    h  = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
