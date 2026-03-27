import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from moviepy.editor import AudioFileClip, VideoClip
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

WIDTH, HEIGHT = 1280, 720
FPS = 24
BG_COLOR = (15, 15, 30)       # Dark navy
WAVE_COLOR = (0, 200, 255)    # Cyan
TEXT_COLOR = (255, 255, 255)  # White
SUB_BG = (30, 30, 60, 180)   # Semi-transparent subtitle bar


def create_animated_mp4(mp3_path: str, segments: list) -> str:
    """Create an animated MP4 with waveform + subtitles from MP3 + Whisper segments."""
    audio_clip = AudioFileClip(mp3_path)
    duration = audio_clip.duration

    # Pre-load audio samples for waveform
    audio_array = audio_clip.to_soundarray(fps=4000)  # low-res for viz
    if audio_array.ndim > 1:
        audio_array = audio_array.mean(axis=1)  # stereo -> mono
    audio_array = audio_array / (np.max(np.abs(audio_array)) + 1e-9)  # normalize

    def get_subtitle_at(t):
        """Return the subtitle text active at time t."""
        for seg in segments:
            if seg["start"] <= t <= seg["end"]:
                return seg["text"].strip()
        return ""

    def make_frame(t):
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img, "RGBA")

        # --- Draw waveform ---
        window = 0.5  # seconds of waveform visible
        center_sample = int(t * 4000)
        half_win = int(window * 4000 // 2)
        start_s = max(0, center_sample - half_win)
        end_s = min(len(audio_array), center_sample + half_win)
        wave_chunk = audio_array[start_s:end_s]

        if len(wave_chunk) > 1:
            x_vals = np.linspace(0, WIDTH, len(wave_chunk))
            mid_y = int(HEIGHT * 0.45)
            amp = HEIGHT * 0.25

            # Glow effect: draw multiple layers
            for glow, alpha_factor in [(6, 40), (3, 80), (1, 220)]:
                pts = [(int(x_vals[i]), int(mid_y + wave_chunk[i] * amp))
                       for i in range(len(wave_chunk))]
                for k in range(len(pts) - 1):
                    x1, y1 = pts[k]
                    x2, y2 = pts[k + 1]
                    color = (WAVE_COLOR[0], WAVE_COLOR[1], WAVE_COLOR[2], alpha_factor)
                    draw.line([x1 - glow, y1, x2 - glow, y2], fill=color, width=glow)

        # --- Progress bar ---
        progress = t / duration
        bar_y = HEIGHT - 20
        draw.rectangle([0, bar_y, int(WIDTH * progress), HEIGHT],
                        fill=(0, 200, 255, 160))

        # --- Subtitle ---
        subtitle = get_subtitle_at(t)
        if subtitle:
            wrapped = textwrap.fill(subtitle, width=60)
            lines = wrapped.split("\n")
            line_h = 38
            total_h = len(lines) * line_h + 20
            sub_y = HEIGHT - 80 - total_h

            draw.rectangle([60, sub_y - 10, WIDTH - 60, sub_y + total_h],
                            fill=SUB_BG)

            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            except Exception:
                font = ImageFont.load_default()

            for j, line in enumerate(lines):
                tw = draw.textlength(line, font=font) if hasattr(draw, 'textlength') else 400
                tx = (WIDTH - tw) // 2
                ty = sub_y + j * line_h
                draw.text((tx, ty), line, font=font, fill=TEXT_COLOR)

        # --- Title ---
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        except Exception:
            title_font = ImageFont.load_default()
        draw.text((20, 15), "🎙 Audio Transcription", font=title_font, fill=(180, 180, 255))

        return np.array(img)

    video_clip = VideoClip(make_frame, duration=duration)
    video_clip = video_clip.set_audio(audio_clip)

    out_path = mp3_path.replace(".mp3", ".mp4")
    video_clip.write_videofile(
        out_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )

    audio_clip.close()
    video_clip.close()
    return out_path
