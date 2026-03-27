import numpy as np
from moviepy.editor import AudioFileClip, VideoClip
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

WIDTH, HEIGHT = 1280, 720
FPS = 15            # 15 fps is visually fine for a talking-head/waveform video
BG_COLOR   = (15, 15, 30)
WAVE_COLOR = (0, 200, 255)
TEXT_COLOR = (255, 255, 255)
SUB_BG     = (30, 30, 60)

WAVE_RATE = 2000   # samples/sec for waveform (low-res is fine visually)


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a TTF font cross-platform."""
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _text_width(draw, text, font):
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]
    except Exception:
        return len(text) * 18


def create_animated_mp4(mp3_path: str, segments: list) -> str:
    audio_clip = AudioFileClip(mp3_path)
    duration   = audio_clip.duration

    # -- Load waveform once at low sample rate --
    audio_arr = audio_clip.to_soundarray(fps=WAVE_RATE)
    if audio_arr.ndim > 1:
        audio_arr = audio_arr.mean(axis=1)
    mx = np.max(np.abs(audio_arr))
    if mx > 0:
        audio_arr /= mx

    # -- Pre-render static background once --
    bg = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)

    # -- Cache fonts (expensive to load per-frame) --
    font_sub   = _get_font(32, bold=True)
    font_title = _get_font(22, bold=False)

    # -- Build subtitle lookup dict keyed by 10ms buckets for O(1) access --
    sub_lookup = {}
    for seg in segments:
        start_b = int(seg["start"] * 100)
        end_b   = int(seg["end"]   * 100)
        for b in range(start_b, end_b + 1):
            sub_lookup[b] = seg["text"].strip()

    half_win = WAVE_RATE // 4   # 0.25s each side

    def make_frame(t):
        frame = bg.copy()
        draw  = ImageDraw.Draw(frame)

        # --- Waveform ---
        center = int(t * WAVE_RATE)
        s = max(0, center - half_win)
        e = min(len(audio_arr), center + half_win)
        chunk = audio_arr[s:e]

        if len(chunk) > 1:
            x_vals = np.linspace(0, WIDTH, len(chunk), dtype=np.float32)
            mid_y  = int(HEIGHT * 0.45)
            amp    = HEIGHT * 0.25
            ys     = (mid_y + chunk * amp).astype(np.int32)

            # Glow layers
            for glow_w, rgb in [
                (7, (0, 60, 80)),
                (4, (0, 120, 160)),
                (2, (0, 180, 220)),
                (1, WAVE_COLOR),
            ]:
                xs = x_vals.astype(np.int32)
                pts = list(zip(xs.tolist(), ys.tolist()))
                for k in range(len(pts) - 1):
                    draw.line([pts[k], pts[k + 1]], fill=rgb, width=glow_w)

        # --- Progress bar ---
        draw.rectangle([0, HEIGHT - 8, int(WIDTH * t / duration), HEIGHT],
                       fill=WAVE_COLOR)

        # --- Subtitle ---
        bucket   = int(t * 100)
        subtitle = sub_lookup.get(bucket, "")
        if subtitle:
            wrapped = textwrap.fill(subtitle, width=58)
            lines   = wrapped.split("\n")
            line_h  = 42
            box_h   = len(lines) * line_h + 24
            box_y   = HEIGHT - 95 - box_h

            # Transparent subtitle bar
            overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            od.rectangle([50, box_y, WIDTH - 50, box_y + box_h],
                         fill=(*SUB_BG, 190))
            frame = Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")
            draw  = ImageDraw.Draw(frame)

            for j, line in enumerate(lines):
                tw = _text_width(draw, line, font_sub)
                tx = max(60, (WIDTH - tw) // 2)
                ty = box_y + 12 + j * line_h
                draw.text((tx + 2, ty + 2), line, font=font_sub, fill=(0, 0, 0))   # shadow
                draw.text((tx,     ty),     line, font=font_sub, fill=TEXT_COLOR)

        # --- Title + timestamp ---
        draw.text((20, 14), "\U0001f399  Audio Transcription",
                  font=font_title, fill=(180, 180, 255))
        ts = f"{int(t // 60):02}:{int(t % 60):02}"
        tw = _text_width(draw, ts, font_title)
        draw.text((WIDTH - tw - 20, 14), ts, font=font_title, fill=(150, 150, 200))

        return np.array(frame)

    video_clip = VideoClip(make_frame, duration=duration)
    video_clip = video_clip.set_audio(audio_clip)

    out_path = os.path.splitext(mp3_path)[0] + "_output.mp4"
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
