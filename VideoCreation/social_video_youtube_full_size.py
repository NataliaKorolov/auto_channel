import os
import pandas as pd
from typing import List, Tuple
from moviepy import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import TextClip
from moviepy import TextClip, CompositeVideoClip, vfx

# No need to import "moviepy.video.fx.all" directly.
# All required effects (like fadein) are imported individually above.
# === CONFIGURATION ===
# BASE = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot\300"
BASE = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot\TragicBraveryHector"
VIDEO_PATHS = [os.path.join(BASE, f"prompt {i}.mp4") for i in range(1, 11)]
AUDIO_PATH = os.path.join(BASE, "Voice_Over_EN.mp3")
CSV_PATH = os.path.join(BASE, "Video_Texts.csv")
FONT_PATH = os.path.join(BASE, "Cinzel-Regular.ttf")  # Update if needed

MIN_DURATION = 40  # seconds
DEFAULT_FONT = "DejaVuSans"  # Safe fallback font

def get_texts_from_csv(csv_path: str) -> List[str]:
    """Read English texts from a CSV file."""
    try:
        df = pd.read_csv(csv_path)
        return df['english_text'].tolist()
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

def add_text_overlay(clip: VideoFileClip, text: str, size: Tuple[int, int]) -> CompositeVideoClip:
    """Overlay centered text on a video clip."""
    try:
        txt_clip = TextClip(
            text=text,
            font=DEFAULT_FONT,
            font_size=50,
            color='#D4AF37',
            stroke_color='black',
            stroke_width=2,
            method="caption",
            size=(int(clip.w * 0.9), None),
            text_align="center",
            vertical_align="center",
            margin=(10, 10, 10, 10)
        ).with_duration(clip.duration)
        # txt_clip = fadein(txt_clip, 1.0)
        position = ("center", int(clip.h * 0.75))
        txt_clip = txt_clip.with_position(position)
        return CompositeVideoClip([clip, txt_clip], size=size).with_duration(clip.duration)
    except Exception as e:
        print(f"Error creating text overlay: {e}")
        return CompositeVideoClip([clip], size=size).with_duration(clip.duration)

def resize_and_crop_clip(clip: VideoFileClip, size: Tuple[int, int], resize_dim: str) -> VideoFileClip:
    """Resize and crop a clip to the target size."""
    if resize_dim == "height":
        clip = clip.resized(height=size[1])
        x1 = max(0, (clip.w - size[0]) // 2)
        x2 = x1 + size[0]
        clip = clip.cropped(x1=x1, x2=x2)
    else:
        clip = clip.resized(width=size[0])
        y1 = max(0, (clip.h - size[1]) // 2)
        y2 = y1 + size[1]
        clip = clip.cropped(y1=y1, y2=y2)
    return clip

def make_and_export(output_file: str, size: Tuple[int, int], resize_dim: str) -> None:
    """Create and export a video with overlaid text and audio."""
    texts = get_texts_from_csv(CSV_PATH)
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
    if final_clip.duration < MIN_DURATION:
        loops = int(MIN_DURATION // final_clip.duration) + 1
        final_clip = concatenate_videoclips([final_clip] * loops, method="compose")
    final_clip = final_clip.subclipped(0, MIN_DURATION)

    try:
        audio_clip = AudioFileClip(AUDIO_PATH).subclipped(0, MIN_DURATION)
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

def make_and_export_blur(output_file: str, size: Tuple[int, int]) -> None:
    """Create and export a video with blurred background effect."""
    try:
        import cv2
    except ImportError:
        print("OpenCV (cv2) is not installed. Please run 'pip install opencv-python'.")
        return

    clips = []
    for path in VIDEO_PATHS:
        if not os.path.exists(path):
            print(f"Warning: {path} not found. Skipping.")
            continue
        try:
            clip = VideoFileClip(path)
            fg_clip = clip.resized(width=size[0])
            if hasattr(clip, 'fl_image'):
                def blur_frame(frame):
                    return cv2.GaussianBlur(frame, (99, 99), 50)
                bg_clip = clip.resized(height=size[1]).fl_image(blur_frame)
                bg_clip = bg_clip.set_position((0, 0)).set_opacity(1)
            else:
                from moviepy.video.VideoClip import ColorClip
                bg_clip = ColorClip(size=size, color=(0, 0, 0)).with_duration(clip.duration)
            fg_y = (size[1] - fg_clip.h) // 2
            fg_clip = fg_clip.set_position((0, fg_y))
            comp = CompositeVideoClip([bg_clip, fg_clip], size=size).set_duration(clip.duration)
            clips.append(comp)
        except Exception as e:
            print(f"Error processing {path}: {e}")

    if not clips:
        print("No video clips found. Exiting.")
        return

    final_clip = concatenate_videoclips(clips, method="compose")
    if final_clip.duration < MIN_DURATION:
        loops = int(MIN_DURATION // final_clip.duration) + 1
        final_clip = concatenate_videoclips([final_clip] * loops, method="compose")
    final_clip = final_clip.subclipped(0, MIN_DURATION)

    try:
        audio_clip = AudioFileClip(AUDIO_PATH).subclipped(0, MIN_DURATION)
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
    # For vertical 1080x1920 output (TikTok/Instagram), use resize_dim="height"
    make_and_export(os.path.join(BASE, "final_vertical_1080x1920.mp4"), (1080, 1920), "height")
    # For horizontal 1920x1080 output (YouTube), use resize_dim="width"
    make_and_export(os.path.join(BASE, "final_horizontal_1920x1080.mp4"), (1920, 1080), "width")

