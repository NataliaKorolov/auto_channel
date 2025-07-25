import os
import pandas as pd
from typing import List, Tuple
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from video_common import CreateAudioFile, CreateVideoFile, ConcatenateAudioFiles, ConcatenateVideoFiles, BASE_DIRECTORY


# No need to import "moviepy.video.fx.all" directly.
# All required effects (like fadein) are imported individually above.
# === CONFIGURATION ===
BASE_DIRECTORY_GREECE = os.path.join(BASE_DIRECTORY, "Greece_Automation")

BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS = os.path.join(BASE_DIRECTORY_GREECE, "Common_Artifacts")

INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS = os.path.join(BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro")

INTRO_AUDIO_OUTPUT_FILE_EN = os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro_Audio_Output_EN.mp3")
INTRO_AUDIO_OUTPUT_FILE_RU = os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro_Audio_Output_RU.mp3")

INTRO_MUSIC_OVERLAY_PATH = os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro_Music.mp3")
INTRO_TEXT_AUDIO_OVERLAY_PATH_EN = os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Welcome_EN_TG.mp3")
INTRO_TEXT_AUDIO_OVERLAY_PATH_RU = os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Welcome_RU_TG.mp3")
INTRO_TEXT_OVERLAY_CSV_PATH = os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro_Text_Overlay_EN_RU.csv")
INTRO_VIDEO_PATHS = [os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, f"Intro_{i}.mp4") for i in range(1, 2)]

INTRO_VIDEO_EN_HORIZONTAL = os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro_Output_horizontal_1920x1080_EN.mp4")
INTRO_VIDEO_RU_HORIZONTAL = os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro_Output_horizontal_1920x1080_RU.mp4")
INTRO_VIDEO_EN_VERTICAL = os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro_Output_vertical_1080x1920_EN.mp4")
INTRO_VIDEO_RU_VERTICAL= os.path.join(INTRO_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro_Output_vertical_1080x1920_RU.mp4")


TAIL_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS = os.path.join(BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Tail")

TAIL_AUDIO_OUTPUT_FILE_EN = os.path.join(TAIL_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Tail_Audio_Output_EN.mp3")
TAIL_AUDIO_OUTPUT_FILE_RU = os.path.join(TAIL_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Tail_Audio_Output_RU.mp3")
TAIL_MUSIC_OVERLAY_PATH = os.path.join(TAIL_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Tail_Music.mp3")
TAIL_TEXT_AUDIO_OVERLAY_PATH_EN = os.path.join(TAIL_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Tail_EN_TG.mp3")
TAIL_TEXT_AUDIO_OVERLAY_PATH_RU = os.path.join(TAIL_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Tail_RU_TG.mp3")   
TAIL_TEXT_OVERLAY_CSV_PATH = os.path.join(TAIL_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Tail_Text_Overlay_EN_RU.csv")
TAIL_VIDEO_PATHS = [os.path.join(TAIL_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, f"Tail_{i}.mp4") for i in range(1, 3)]
# TAIL_OUTPUT_FILE = os.path.join(TAIL_BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Tail_Output.mp4")



BASE_DIRECTORY_GREECE_CURRENT = os.path.join(BASE_DIRECTORY_GREECE, "TragicBraveryHector")
VIDEO_PATHS = [os.path.join(BASE_DIRECTORY_GREECE_CURRENT, f"prompt {i}.mp4") for i in range(1, 11)]
AUDIO_PATH_RU = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Voice_Over_RU.mp3")
AUDIO_PATH_EN = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Voice_Over_EN.mp3")

AUDIO_PATH_WITH_TAIL_RU = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Voice_Over_RU_With_Tail.mp3")
AUDIO_PATH_WITH_TAIL_EN = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Voice_Over_EN_With_Tail.mp3")

CSV_PATH = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Video_Texts.csv")

VIDEO_EN_HORIZONTAL_MAIN_PLUS_TAIL = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "main_plus_tail_horizontal_1920x1080_EN.mp4")
VIDEO_RU_HORIZONTAL_MAIN_PLUS_TAIL = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "main_plus_tail_horizontal_1920x1080_RU.mp4")
VIDEO_EN_VERTICAL_MAIN_PLUS_TAIL = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "main_plus_tail_vertical_1080x1920_EN.mp4")
VIDEO_RU_VERTICAL_MAIN_PLUS_TAIL = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "main_plus_tail_vertical_1080x1920_RU.mp4")

FINAL_VIDEO_EN_HORIZONTAL = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "final_horizontal_1920x1080_EN.mp4")
FINAL_VIDEO_RU_HORIZONTAL = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "final_horizontal_1920x1080_RU.mp4")
FINAL_VIDEO_EN_VERTICAL = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "final_vertical_1080x1920_EN.mp4")
FINAL_VIDEO_RU_VERTICAL = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "final_vertical_1080x1920_RU.mp4")


# FONT_PATH = os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "Cinzel-Regular.ttf")  # Update if needed

DEFAULT_FONT = "DejaVuSans"  # Safe fallback font


if __name__ == "__main__":

    # """ final_horizontal_1920x1080_EN  """

    # Intro: first create the audio file
    CreateAudioFile(
        output_file=INTRO_AUDIO_OUTPUT_FILE_EN,
        music_overlay_path=INTRO_MUSIC_OVERLAY_PATH,
        text_audio_overlay_path=INTRO_TEXT_AUDIO_OVERLAY_PATH_EN,
        set_duration_by_text_audio=True,
        time_of_music_before_voice=0.2,  # seconds of music before voice starts
        time_of_music_after_voice=1.5  # Adjust as needed
   )
    
    # Intro: Create video
    CreateVideoFile(
        output_file=INTRO_VIDEO_EN_HORIZONTAL,
        size=(1920, 1080),
        resize_dim="width",
        audio_path=INTRO_AUDIO_OUTPUT_FILE_EN,  # Simple audio file, not prepared audio
        csv_path=INTRO_TEXT_OVERLAY_CSV_PATH,      # CSV file with texts
        text_column="english_text",
        video_paths=INTRO_VIDEO_PATHS,
        use_audio_duration=False  # Add this flag to use audio duration
    ) 

   # TAIL: first create the audio file
    CreateAudioFile(
        output_file=TAIL_AUDIO_OUTPUT_FILE_EN,
        music_overlay_path=TAIL_MUSIC_OVERLAY_PATH,
        text_audio_overlay_path=TAIL_TEXT_AUDIO_OVERLAY_PATH_EN,
        set_duration_by_text_audio=True,        
        time_of_music_before_voice=2,  # 0.8 seconds of music before voice starts
        time_of_music_after_voice=2  # Adjust as needed
    )

    # MAin + Tail: Apply effects during concatenation
    ConcatenateAudioFiles(
        audio_paths=[AUDIO_PATH_EN, TAIL_AUDIO_OUTPUT_FILE_EN],
        output_file=AUDIO_PATH_WITH_TAIL_EN,
        silence_between=0.5  # seconds of silence between main audio and tail
    )


    CreateVideoFile(
        output_file=VIDEO_EN_HORIZONTAL_MAIN_PLUS_TAIL,
        size=(1920, 1080),
        resize_dim="width",
        audio_path=AUDIO_PATH_WITH_TAIL_EN,
        csv_path=[CSV_PATH, TAIL_TEXT_OVERLAY_CSV_PATH],  # Now accepts a list of paths
        text_column="english_text",
        video_paths=VIDEO_PATHS + TAIL_VIDEO_PATHS,
        use_audio_duration=True  # Add this flag to use audio duration
    ) 

    ConcatenateVideoFiles(
        video_paths=[
            INTRO_VIDEO_EN_HORIZONTAL,
            VIDEO_EN_HORIZONTAL_MAIN_PLUS_TAIL
        ],
        output_file=FINAL_VIDEO_EN_HORIZONTAL,
    )












    # # Russian versions
    # CreateVideoFile(
    #     os.path.join(BASE_DIRECTORY_GREECE_CURRENT, "final_vertical_1080x1920_RU.mp4"),
    #     (1080, 1920),
    #     "height",
    #     AUDIO_PATH_RU,
    #     CSV_PATH,
    #     "russian_text",
    #     VIDEO_PATHS,
    #     use_audio_duration=False  # Add this flag to use audio duration
    # )
    




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

