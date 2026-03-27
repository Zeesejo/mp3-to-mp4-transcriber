import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip
import subprocess
import os
import textwrap
import sys

WIDTH, HEIGHT = 1280, 720
FPS = 15
BG_COLOR   = (15, 15, 30)
WAVE_COLOR = (0, 200, 255)
TEXT_COLOR = (255, 255, 255)
SUB_BG     = (30, 30, 60)
WAVE_RATE  = 2000  # audio samples/sec for waveform viz


def _get_font(size, bold=False):
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


def _text_w(draw, text, font):
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]
    except Exception:
        return len(text) * 18


def create_animated_mp4(mp3_path: str, segments: list) -> str:
    audio_clip = AudioFileClip(mp3_path)
    duration   = audio_clip.duration
    total_frames = int(duration * FPS)

    # Load waveform at low rate
    audio_arr = audio_clip.to_soundarray(fps=WAVE_RATE)
    if audio_arr.ndim > 1:
        audio_arr = audio_arr.mean(axis=1)
    mx = np.max(np.abs(audio_arr))
    if mx > 0:
        audio_arr /= mx
    audio_clip.close()

    # O(1) subtitle lookup
    sub_lookup = {}
    for seg in segments:
        for b in range(int(seg["start"] * FPS), int(seg["end"] * FPS) + 1):
            sub_lookup[b] = seg["text"].strip()

    # Cache fonts & background
    font_sub   = _get_font(32, bold=True)
    font_title = _get_font(22)
    bg         = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    half_win   = WAVE_RATE // 4

    out_path = os.path.splitext(mp3_path)[0] + "_output.mp4"

    # --- ffmpeg pipe: raw RGB frames in, H264+AAC out ---
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "pipe:0",          # video from stdin
        "-i", mp3_path,           # audio from file
        "-c:v", "libx264",
        "-preset", "ultrafast",   # fastest encode
        "-crf", "23",
        "-c:a", "aac",
        "-shortest",
        "-pix_fmt", "yuv420p",
        out_path
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    print(f"Rendering {total_frames} frames at {FPS} fps...", flush=True)

    for frame_idx in range(total_frames):
        t = frame_idx / FPS

        frame = bg.copy()
        draw  = ImageDraw.Draw(frame)

        # Waveform
        center = int(t * WAVE_RATE)
        s = max(0, center - half_win)
        e = min(len(audio_arr), center + half_win)
        chunk = audio_arr[s:e]
        if len(chunk) > 1:
            xs = np.linspace(0, WIDTH, len(chunk), dtype=np.float32)
            mid_y = int(HEIGHT * 0.45)
            amp   = HEIGHT * 0.25
            ys    = (mid_y + chunk * amp).astype(np.int32)
            for glow_w, rgb in [(7,(0,50,70)),(4,(0,120,160)),(2,(0,170,210)),(1,WAVE_COLOR)]:
                pts = list(zip(xs.astype(int).tolist(), ys.tolist()))
                for k in range(len(pts) - 1):
                    draw.line([pts[k], pts[k+1]], fill=rgb, width=glow_w)

        # Progress bar
        draw.rectangle([0, HEIGHT-8, int(WIDTH * t / duration), HEIGHT], fill=WAVE_COLOR)

        # Subtitle
        subtitle = sub_lookup.get(frame_idx, "")
        if subtitle:
            wrapped = textwrap.fill(subtitle, width=58)
            lines   = wrapped.split("\n")
            line_h  = 42
            box_h   = len(lines) * line_h + 24
            box_y   = HEIGHT - 95 - box_h
            overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
            od = ImageDraw.Draw(overlay)
            od.rectangle([50, box_y, WIDTH-50, box_y+box_h], fill=(*SUB_BG, 190))
            frame = Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")
            draw  = ImageDraw.Draw(frame)
            for j, line in enumerate(lines):
                tw = _text_w(draw, line, font_sub)
                tx = max(60, (WIDTH - tw) // 2)
                ty = box_y + 12 + j * line_h
                draw.text((tx+2, ty+2), line, font=font_sub, fill=(0,0,0))
                draw.text((tx,   ty),   line, font=font_sub, fill=TEXT_COLOR)

        # Title & timestamp
        draw.text((20, 14), "\U0001f399  Audio Transcription", font=font_title, fill=(180,180,255))
        ts = f"{int(t//60):02}:{int(t%60):02}"
        tw = _text_w(draw, ts, font_title)
        draw.text((WIDTH-tw-20, 14), ts, font=font_title, fill=(150,150,200))

        proc.stdin.write(frame.tobytes())

        # Progress log every 5 seconds worth of frames
        if frame_idx % (FPS * 5) == 0:
            pct = frame_idx / total_frames * 100
            elapsed_s = frame_idx / FPS
            print(f"  {pct:.1f}%  ({int(elapsed_s//60):02}:{int(elapsed_s%60):02} / "
                  f"{int(duration//60):02}:{int(duration%60):02})", flush=True)

    proc.stdin.close()
    proc.wait()
    print(f"Done! Saved to: {out_path}", flush=True)
    return out_path
