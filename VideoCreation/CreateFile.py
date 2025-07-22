import os
from typing import List
from video_common import CreateVideoFile, BASE_DIRECTORY

# Example usage of CreateVideoFile
if __name__ == "__main__":
    # Define paths relative to BASE_DIRECTORY
    VIDEO_PATHS = [os.path.join("Common_Artifacts", "Intro", f"Intro_{i}.mp4") for i in range(1, 11)]
    
    # Call CreateVideoFile with example parameters
    CreateVideoFile(
        output_file=os.path.join("Common_Artifacts", "Intro", "Intro_Output.mp4"),
        video_paths=VIDEO_PATHS,
        music_overlay_path=os.path.join("Common_Artifacts", "Intro", "Intro_Music.mp3"),
        text_audio_overlay_path=os.path.join("Common_Artifacts", "Intro", "Intro_Text.mp3"),
        overlays_xlsx_path=os.path.join("Common_Artifacts", "Intro", "Intro_Text_Overlay.xlsx"),
        size=(1920, 1080),
        resize_dim="width",
        text_column="english_text"
    )