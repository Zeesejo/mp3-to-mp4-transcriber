import whisper
import torch
import os

def transcribe_audio(mp3_path: str, model_size: str = "base"):
    """
    Transcribe an MP3 using OpenAI Whisper.
    Automatically uses CUDA GPU if available, else CPU.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Whisper device: {device} ({torch.cuda.get_device_name(0) if device == 'cuda' else 'CPU'})", flush=True)

    model = whisper.load_model(model_size, device=device)
    result = model.transcribe(mp3_path, verbose=False, fp16=(device == "cuda"))
    segments = result["segments"]

    srt_path = os.path.splitext(mp3_path)[0] + ".srt"
    _write_srt(segments, srt_path)

    return segments, srt_path


def _write_srt(segments, srt_path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n{_fmt(seg['start'])} --> {_fmt(seg['end'])}\n{seg['text'].strip()}\n\n")


def _fmt(seconds: float) -> str:
    ms = int(round((seconds % 1) * 1000))
    s  = int(seconds) % 60
    m  = int(seconds // 60) % 60
    h  = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
