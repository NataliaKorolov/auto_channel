import os
from typing import List
from video_common import BASE_DIRECTORY, CreateAudioFile, CreateVideoFile

# Example usage of CreateVideoFile
if __name__ == "__main__":
    # Define paths relative to BASE_DIRECTORY
    BASE_DIRECTORY_GREECE = os.path.join(BASE_DIRECTORY, "Greece_Automation")
    AUDIO_OUTPUT_FILE = os.path.join(BASE_DIRECTORY_GREECE, "Common_Artifacts", "Intro", "Intro_Audio_Output.mp3")
    MUSIC_OVERLAY_PATH = os.path.join(BASE_DIRECTORY_GREECE, "Common_Artifacts", "Intro", "Intro_Music.mp3")
    TEXT_AUDIO_OVERLAY_PATH = os.path.join(BASE_DIRECTORY_GREECE, "Common_Artifacts", "Intro", "Intro_Text.mp3")
    CSV_PATH = os.path.join(BASE_DIRECTORY_GREECE, "Common_Artifacts", "Intro", "Intro_Text_Overlay_EN_RU.csv")
    VIDEO_PATHS = [os.path.join(BASE_DIRECTORY_GREECE, "Common_Artifacts", "Intro", f"Intro_{i}.mp4") for i in range(1, 11)]
    OUTPUT_FILE = os.path.join(BASE_DIRECTORY_GREECE, "Common_Artifacts", "Intro", "Intro_Output.mp4")

    # First create the prepared audio file
    CreateAudioFile(
        output_file=AUDIO_OUTPUT_FILE,
        music_overlay_path=MUSIC_OVERLAY_PATH,
        text_audio_overlay_path=TEXT_AUDIO_OVERLAY_PATH
    )
    
    # Create video using CreateVideoFile
    CreateVideoFile(
        output_file=OUTPUT_FILE,
        size=(1920, 1080),
        resize_dim="width",
        audio_path=AUDIO_OUTPUT_FILE,  # Simple audio file, not prepared audio
        csv_path=CSV_PATH,      # CSV file with texts
        text_column="english_text",
        video_paths=VIDEO_PATHS,
        use_audio_duration=True  # Add this flag to use audio duration
    ) 

