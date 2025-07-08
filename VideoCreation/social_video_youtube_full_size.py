import os
import pandas as pd
from typing import List, Tuple
from moviepy import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import TextClip
from moviepy import TextClip, CompositeVideoClip
from video_common import get_texts_from_csv, add_text_overlay, resize_and_crop_clip


# No need to import "moviepy.video.fx.all" directly.
# All required effects (like fadein) are imported individually above.
# === CONFIGURATION ===
# BASE = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot\300"
BASE = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot\TragicBraveryHector"
VIDEO_PATHS = [os.path.join(BASE, f"prompt {i}.mp4") for i in range(1, 11)]
AUDIO_PATH_RU = os.path.join(BASE, "Voice_Over_RU.mp3")
AUDIO_PATH_EN = os.path.join(BASE, "Voice_Over_EN.mp3")
CSV_PATH = os.path.join(BASE, "Video_Texts.csv")
FONT_PATH = os.path.join(BASE, "Cinzel-Regular.ttf")  # Update if needed

MIN_DURATION = 40  # seconds
DEFAULT_FONT = "DejaVuSans"  # Safe fallback font

def make_and_export(output_file: str, size: Tuple[int, int], resize_dim: str, audio_path: str, csv_path: str, text_column: str) -> None:
    """Create and export a video with overlaid text and audio."""
    texts = get_texts_from_csv(csv_path, text_column)
    clips = []
    for idx, path in enumerate(VIDEO_PATHS):
        if not os.path.exists(path):
            print(f"Warning: {path} not found. Skipping.")
            continue
        try:
            clip = VideoFileClip(path)
            clip = resize_and_crop_clip(clip, size, resize_dim)
            if idx < len(texts):
                clip = add_text_overlay(clip, texts[idx], size)
            else:
                print(f"Warning: No text for clip {idx+1}")
            clips.append(clip)
        except Exception as e:
            print(f"Error processing {path}: {e}")

    if not clips:
        print("No video clips found. Exiting.")
        return

    final_clip = concatenate_videoclips(clips, method="compose")
    video_duration = final_clip.duration

    if video_duration < MIN_DURATION:
        print(f"Warning: Final video duration ({video_duration:.2f}s) is shorter than MIN_DURATION ({MIN_DURATION}s).")
    else:
        print(f"Final video duration: {video_duration:.2f}s")

    try:
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        if audio_duration > video_duration:
            print(f"Warning: Audio duration ({audio_duration:.2f}s) is longer than video duration ({video_duration:.2f}s). Audio will be cut to video length.")
            audio_clip = audio_clip.set_duration(video_duration)
        final_with_audio = final_clip.with_audio(audio_clip)
        final_with_audio.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            bitrate="20000k",
            audio_fps=44100,
            logger=None,
            threads=4
        )
    except Exception as e:
        print(f"Error exporting video: {e}")

if __name__ == "__main__":
    # Russian versions
    make_and_export(
        os.path.join(BASE, "final_vertical_1080x1920_RU.mp4"),
        (1080, 1920),
        "height",
        AUDIO_PATH_RU,
        CSV_PATH,
        "russian_text"
    )
    make_and_export(
        os.path.join(BASE, "final_horizontal_1920x1080_RU.mp4"),
        (1920, 1080),
        "width",
        AUDIO_PATH_RU,
        CSV_PATH,
        "russian_text"
    )
    # English versions
    make_and_export(
        os.path.join(BASE, "final_vertical_1080x1920_EN.mp4"),
        (1080, 1920),
        "height",
        AUDIO_PATH_EN,
        CSV_PATH,
        "english_text"
    )
    make_and_export(
        os.path.join(BASE, "final_horizontal_1920x1080_EN.mp4"),
        (1920, 1080),
        "width",
        AUDIO_PATH_EN,
        CSV_PATH,
        "english_text"
    )

