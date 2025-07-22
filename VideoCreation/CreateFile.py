import os
from typing import List
from video_common import CreateVideoFile, BASE_DIRECTORY, CreateAudioFile

# Example usage of CreateVideoFile
if __name__ == "__main__":
    # Define paths relative to BASE_DIRECTORY
    AUDIO_OUTPUT_FILE = os.path.join(BASE_DIRECTORY, "Common_Artifacts", "Intro", "Intro_Audio_Output.mp3")
    MUSIC_OVERLAY_PATH = os.path.join(BASE_DIRECTORY, "Common_Artifacts", "Intro", "Intro_Music.mp3")
    TEXT_AUDIO_OVERLAY_PATH = os.path.join(BASE_DIRECTORY, "Common_Artifacts", "Intro", "Intro_Text.mp3")
    # VIDEO_PATHS = [os.path.join("Common_Artifacts", "Intro", f"Intro_{i}.mp4") for i in range(1, 11)]
    
    # # Call CreateVideoFile with example parameters
    # CreateVideoFile(
    #     output_file=os.path.join("Common_Artifacts", "Intro", "Intro_Output.mp4"),
    #     video_paths=VIDEO_PATHS,
    #     music_overlay_path=os.path.join("Common_Artifacts", "Intro", "Intro_Music.mp3"),
    #     text_audio_overlay_path=os.path.join("Common_Artifacts", "Intro", "Intro_Text.mp3"),
    #     overlays_xlsx_path=os.path.join("Common_Artifacts", "Intro", "Intro_Text_Overlay.xlsx"),
    #     size=(1920, 1080),
    #     resize_dim="width",
    #     text_column="english_text"
    # )

    # Example usage of CreateAudioFile
    CreateAudioFile(
        output_file=AUDIO_OUTPUT_FILE,
        music_overlay_path=MUSIC_OVERLAY_PATH,
        text_audio_overlay_path=TEXT_AUDIO_OVERLAY_PATH
    )

