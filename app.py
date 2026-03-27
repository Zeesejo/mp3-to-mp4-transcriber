import gradio as gr
from transcriber import transcribe_audio
from video_maker import create_animated_mp4
import os

MODEL_CHOICES = ["tiny", "base", "small", "medium", "large"]

SOCIAL_LINKS = """
<div style="text-align:center; padding: 20px 0 10px 0; font-family: sans-serif;">

  <p style="font-size:15px; font-weight:bold; color:#ccc; margin-bottom:10px;">🎙️ Litens Talk</p>
  <p style="font-size:13px; margin-bottom: 6px;">
    <a href="https://youtube.com/@Litends" target="_blank"
       style="margin:0 8px; color:#FF0000; text-decoration:none;">▶️ YouTube</a>
    <a href="https://instagram.com/litendsco" target="_blank"
       style="margin:0 8px; color:#E1306C; text-decoration:none;">📸 Instagram</a>
    <a href="https://facebook.com/profile.php?id=61576822259468" target="_blank"
       style="margin:0 8px; color:#1877F2; text-decoration:none;">📘 Facebook</a>
    <a href="https://linkedin.com/company/litends" target="_blank"
       style="margin:0 8px; color:#0A66C2; text-decoration:none;">💼 LinkedIn</a>
    <a href="https://open.spotify.com/show/7Gm4QCvLZI8qfnBoESAub4" target="_blank"
       style="margin:0 8px; color:#1DB954; text-decoration:none;">🎵 Spotify</a>
    <a href="https://litends.com" target="_blank"
       style="margin:0 8px; color:#aaa; text-decoration:none;">🌐 litends.com</a>
  </p>

  <p style="font-size:12px; color:#666; margin: 12px 0 4px 0;">Built by <strong>Zeeshan</strong></p>
  <p style="font-size:12px; margin-bottom: 4px;">
    <a href="https://instagram.com/zeesejo" target="_blank"
       style="margin:0 6px; color:#E1306C; text-decoration:none;">📸 @zeesejo</a>
    <a href="https://linkedin.com/in/zeesejo" target="_blank"
       style="margin:0 6px; color:#0A66C2; text-decoration:none;">💼 LinkedIn</a>
    <a href="https://youtube.com/c/ZeeseJones" target="_blank"
       style="margin:0 6px; color:#FF0000; text-decoration:none;">▶️ YouTube</a>
  </p>

  <p style="font-size:11px; color:#555; margin-top: 10px;">
    Transcribed with our own open-source tool —
    <a href="https://github.com/Zeesejo/mp3-to-mp4-transcriber" target="_blank"
       style="color:#777; text-decoration:none;">github.com/Zeesejo/mp3-to-mp4-transcriber</a>
  </p>
</div>
"""

ABOUT_TEXT = """
### About This Tool
This tool was built by **Zeeshan (Litens)** to transcribe podcast episodes using
[OpenAI Whisper](https://github.com/openai/whisper) and render an animated MP4 with
waveform visualization and synced subtitles — fully offline, no API key needed.

**Pipeline:** MP3 → Whisper (GPU/CPU) → Subtitle correction → Animated MP4 via FFmpeg

> *"This very episode was transcribed using our own project."* — Zeeshan, Litens Talk Ep.
"""

css = """
.gradio-container { max-width: 900px !important; margin: auto; }
#title-bar { background: linear-gradient(90deg, #0f0f1e, #1a1a3e);
             border-radius: 12px; padding: 20px 28px; margin-bottom: 16px; }
#title-bar h1 { color: #00c8ff; margin: 0; font-size: 26px; }
#title-bar p  { color: #aaa; margin: 4px 0 0 0; font-size: 14px; }
.run-btn { background: linear-gradient(90deg,#00c8ff,#7b61ff) !important;
           color: #fff !important; font-weight: bold !important;
           border-radius: 8px !important; font-size: 15px !important; }
"""

def process_audio(mp3_file, model_size):
    if mp3_file is None:
        return None, None, "⚠️ Please upload an MP3 file."
    print(f"[1/2] Transcribing with Whisper '{model_size}'...")
    try:
        segments, srt_path = transcribe_audio(mp3_file, model_size)
    except Exception as e:
        return None, None, f"❌ Transcription failed: {e}"
    print("[2/2] Rendering animated MP4...")
    try:
        mp4_path = create_animated_mp4(mp3_file, segments)
    except Exception as e:
        return None, None, f"❌ Video rendering failed: {e}"
    full_text = " ".join(s["text"].strip() for s in segments)
    return mp4_path, srt_path, full_text


with gr.Blocks(title="Litens Talk — MP3 Transcriber") as demo:

    gr.HTML("""
    <div id="title-bar">
      <h1>🎙️ Litens Talk — MP3 Transcriber</h1>
      <p>Upload a podcast episode → auto-transcribe with Whisper → export animated MP4 with waveform &amp; subtitles</p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            audio_input = gr.Audio(type="filepath", label="📂 Upload MP3")
        with gr.Column(scale=1):
            model_dd = gr.Dropdown(
                choices=MODEL_CHOICES, value="base",
                label="🤖 Whisper Model",
                info="tiny=fastest · large=most accurate"
            )

    run_btn = gr.Button("▶  Transcribe & Generate Video", variant="primary")

    with gr.Row():
        video_out = gr.Video(label="🎬 Animated MP4")
        srt_out   = gr.File(label="📄 Download .srt Subtitles")

    transcript_box = gr.Textbox(
        label="📝 Full Transcript",
        lines=8,
        placeholder="Your transcript will appear here after processing...",
        interactive=False
    )

    with gr.Accordion("ℹ️ About this project", open=False):
        gr.Markdown(ABOUT_TEXT)

    gr.HTML(SOCIAL_LINKS)

    run_btn.click(
        fn=process_audio,
        inputs=[audio_input, model_dd],
        outputs=[video_out, srt_out, transcript_box]
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), css=css)
