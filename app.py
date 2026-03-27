import gradio as gr
from transcriber import transcribe_audio
from video_maker import create_animated_mp4
import os

MODEL_CHOICES = ["tiny", "base", "small", "medium", "large"]

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


with gr.Blocks(title="MP3 → Animated MP4", theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 🎙️ MP3 Transcriber + Animated MP4 Generator")
    gr.Markdown(
        "Upload an MP3 → get a **Whisper transcription**, "
        "an animated **MP4 with waveform + subtitles**, and a **.srt file**."
    )

    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="📂 Upload MP3")
        model_dd = gr.Dropdown(
            choices=MODEL_CHOICES, value="base",
            label="Whisper Model",
            info="tiny=fastest · large=most accurate"
        )

    run_btn = gr.Button("▶ Transcribe & Generate Video", variant="primary")

    with gr.Row():
        video_out = gr.Video(label="🎬 Animated MP4")
        srt_out   = gr.File(label="📄 Subtitles (.srt)")

    transcript_box = gr.Textbox(
        label="📝 Full Transcript", lines=6,
        placeholder="Transcript will appear here after processing...",
        interactive=False
    )

    run_btn.click(
        fn=process_audio,
        inputs=[audio_input, model_dd],
        outputs=[video_out, srt_out, transcript_box]
    )

if __name__ == "__main__":
    demo.launch()
