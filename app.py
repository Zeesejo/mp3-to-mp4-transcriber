import gradio as gr
from transcriber import transcribe_audio
from video_maker import create_animated_mp4
import os

def process_audio(mp3_file):
    print("[1/2] Transcribing audio...")
    segments, srt_path = transcribe_audio(mp3_file)

    print("[2/2] Creating animated MP4...")
    mp4_path = create_animated_mp4(mp3_file, segments)

    return mp4_path, srt_path

with gr.Blocks(title="MP3 → Animated MP4") as demo:
    gr.Markdown("## 🎙️ MP3 Transcriber + Animated MP4 Generator")
    gr.Markdown("Upload an MP3 file to get a transcription and an animated video with waveform and subtitles.")

    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="Upload MP3")

    with gr.Row():
        run_btn = gr.Button("▶ Transcribe & Generate Video", variant="primary")

    with gr.Row():
        video_out = gr.Video(label="Animated MP4")
        srt_out = gr.File(label="Subtitles (.srt)")

    run_btn.click(fn=process_audio, inputs=audio_input, outputs=[video_out, srt_out])

if __name__ == "__main__":
    demo.launch()
