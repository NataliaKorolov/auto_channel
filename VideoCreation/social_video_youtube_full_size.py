import os
import pandas as pd
from typing import List, Tuple
from moviepy import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
# from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
# from moviepy.video.VideoClip import TextClip
# from moviepy import TextClip, CompositeVideoClip
from video_common import get_texts_from_csv, add_text_overlay, resize_and_crop_clip, CreateVideoFile, BASE_DIRECTORY


# No need to import "moviepy.video.fx.all" directly.
# All required effects (like fadein) are imported individually above.
# === CONFIGURATION ===
BASE_DIRECTORY_GREECE = os.path.join(BASE_DIRECTORY, "Greece_Automation")

BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS = os.path.join(BASE_DIRECTORY_GREECE, "Common_Artifacts")
BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS_TAIL = os.path.join(BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Subscribe")


BASE_DIRECTORY_GREECE_CURRENT = os.path.join(BASE_DIRECTORY_GREECE, "TragicBraveryHector")
VIDEO_PATHS = [os.path.join(BASE_DIRECTORY_GREECE_CURRENT, f"prompt {i}.mp4") for i in range(1, 11)]
AUDIO_PATH_RU = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Voice_Over_RU.mp3")
AUDIO_PATH_EN = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Voice_Over_EN.mp3")
CSV_PATH = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Video_Texts.csv")
# FONT_PATH = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Cinzel-Regular.ttf")  # Update if needed

DEFAULT_FONT = "DejaVuSans"  # Safe fallback font


if __name__ == "__main__":
    # Russian versions
    CreateVideoFile(
        os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "final_vertical_1080x1920_RU.mp4"),
        (1080, 1920),
        "height",
        AUDIO_PATH_RU,
        CSV_PATH,
        "russian_text",
        VIDEO_PATHS,
        use_audio_duration=False  # Add this flag to use audio duration
    )
    
    # CreateVideoFile(
    #     os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "final_horizontal_1920x1080_RU.mp4"),
    #     (1920, 1080),
    #     "width",
    #     AUDIO_PATH_RU,
    #     CSV_PATH,
    #     "russian_text",
    #     VIDEO_PATHS,
    #     use_audio_duration=False  # Add this flag to use audio duration
    # ) 
    
    # # English versions
    # CreateVideoFile(
    #     os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "final_vertical_1080x1920_EN.mp4"),
    #     (1080, 1920),
    #     "height",
    #     AUDIO_PATH_EN, 
    #     CSV_PATH,
    #     "english_text",
    #     VIDEO_PATHS,
    #     use_audio_duration=False  # Add this flag to use audio duration
    # ) 
    # CreateVideoFile(
    #     os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "final_horizontal_1920x1080_EN.mp4"),
    #     (1920, 1080),
    #     "width",
    #     AUDIO_PATH_EN,
    #     CSV_PATH,
    #     "english_text",
    #     VIDEO_PATHS,
    #     use_audio_duration=False  # Add this flag to use audio duration
    # ) 

