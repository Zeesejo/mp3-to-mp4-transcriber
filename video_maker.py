import numpy as np
import matplotlib
matplotlib.use("Agg")
from moviepy.editor import AudioFileClip, VideoClip
from PIL import Image, ImageDraw, ImageFont
import os
import sys
import textwrap

WIDTH, HEIGHT = 1280, 720
FPS = 24
BG_COLOR = (15, 15, 30)
WAVE_COLOR = (0, 200, 255)
TEXT_COLOR = (255, 255, 255)
SUB_BG_COLOR = (30, 30, 60)


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a TTF font cross-platform (Windows / Linux / macOS)."""
    # Windows system fonts
    win_fonts = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ]
    # Linux fonts
    linux_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    # macOS fonts
    mac_fonts = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]

    for path in win_fonts + linux_fonts + mac_fonts:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def create_animated_mp4(mp3_path: str, segments: list) -> str:
    """Create an animated MP4 with waveform + subtitles."""
    audio_clip = AudioFileClip(mp3_path)
    duration = audio_clip.duration

    # Load audio as numpy array for waveform visualization
    audio_array = audio_clip.to_soundarray(fps=4000)
    if audio_array.ndim > 1:
        audio_array = audio_array.mean(axis=1)
    # Normalize safely
    max_val = np.max(np.abs(audio_array))
    audio_array = audio_array / (max_val if max_val > 0 else 1.0)

    font_sub = _get_font(32, bold=True)
    font_title = _get_font(22, bold=False)

    def get_subtitle_at(t):
        for seg in segments:
            if seg["start"] <= t <= seg["end"]:
                return seg["text"].strip()
        return ""

    def make_frame(t):
        # Base layer — opaque RGB
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)

        # --- Waveform ---
        window_samples = int(0.5 * 4000)
        center = int(t * 4000)
        s = max(0, center - window_samples // 2)
        e = min(len(audio_array), center + window_samples // 2)
        chunk = audio_array[s:e]

        if len(chunk) > 1:
            x_vals = np.linspace(0, WIDTH, len(chunk))
            mid_y = int(HEIGHT * 0.45)
            amp = HEIGHT * 0.25

            # Draw glow layers (semi-transparent via blending)
            for glow_w, opacity in [(8, 0.10), (4, 0.25), (2, 0.55), (1, 1.0)]:
                layer = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
                ld = ImageDraw.Draw(layer)
                r = int(WAVE_COLOR[0] * opacity)
                g = int(WAVE_COLOR[1] * opacity)
                b = int(WAVE_COLOR[2] * opacity)
                pts = [(int(x_vals[i]), int(mid_y + chunk[i] * amp))
                       for i in range(len(chunk))]
                for k in range(len(pts) - 1):
                    ld.line([pts[k], pts[k + 1]], fill=(r, g, b), width=glow_w)
                img = Image.blend(img, layer, alpha=0.6 if glow_w > 1 else 1.0)

        draw = ImageDraw.Draw(img)

        # --- Progress bar ---
        progress = t / max(duration, 0.001)
        draw.rectangle([0, HEIGHT - 8, int(WIDTH * progress), HEIGHT],
                       fill=(0, 200, 255))

        # --- Subtitle overlay ---
        subtitle = get_subtitle_at(t)
        if subtitle:
            wrapped = textwrap.fill(subtitle, width=58)
            lines = wrapped.split("\n")
            line_h = 42
            box_h = len(lines) * line_h + 24
            box_y = HEIGHT - 90 - box_h

            # Semi-transparent subtitle background via alpha composite
            overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            od.rectangle([50, box_y, WIDTH - 50, box_y + box_h],
                         fill=(SUB_BG_COLOR[0], SUB_BG_COLOR[1], SUB_BG_COLOR[2], 190))
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
            draw = ImageDraw.Draw(img)

            for j, line in enumerate(lines):
                try:
                    bbox = draw.textbbox((0, 0), line, font=font_sub)
                    tw = bbox[2] - bbox[0]
                except Exception:
                    tw = len(line) * 18
                tx = max(60, (WIDTH - tw) // 2)
                ty = box_y + 12 + j * line_h
                # Shadow
                draw.text((tx + 2, ty + 2), line, font=font_sub, fill=(0, 0, 0))
                draw.text((tx, ty), line, font=font_sub, fill=TEXT_COLOR)

        # --- Title label ---
        draw.text((20, 14), "\U0001f399  Audio Transcription", font=font_title,
                  fill=(180, 180, 255))

        # --- Timestamp ---
        ts = f"{int(t // 60):02}:{int(t % 60):02}"
        try:
            bbox = draw.textbbox((0, 0), ts, font=font_title)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 60
        draw.text((WIDTH - tw - 20, 14), ts, font=font_title, fill=(150, 150, 200))

        return np.array(img)

    video_clip = VideoClip(make_frame, duration=duration)
    video_clip = video_clip.set_audio(audio_clip)

    out_path = mp3_path.replace(".mp3", ".mp4")
    if out_path == mp3_path:
        out_path = mp3_path + "_output.mp4"

    video_clip.write_videofile(
        out_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        logger=None,
        threads=4,
    )

    audio_clip.close()
    video_clip.close()
    return out_path
