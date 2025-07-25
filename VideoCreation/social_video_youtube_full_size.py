import os
from video_common import CreateAudioFile, CreateVideoFile, ConcatenateAudioFiles, ConcatenateVideoFiles, BASE_DIRECTORY

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


def create_complete_video_for_greece(language: str, orientation: str):
    """
    Creates a complete video with intro, main content, and tail for the specified language and orientation.
    
    Args:
        language: Language code ("EN" or "RU")
        orientation: Video orientation ("horizontal" or "vertical")
    """
    print(f"\n=== Creating {language} {orientation} video ===")
    
    # Define dimensions based on orientation
    if orientation == "horizontal":
        size = (1920, 1080)
        resize_dim = "width"
    else:  # vertical
        size = (1080, 1920)
        resize_dim = "height"
        
    # Define language-specific variables
    text_column = "english_text" if language == "EN" else "russian_text"
    intro_audio = INTRO_AUDIO_OUTPUT_FILE_EN if language == "EN" else INTRO_AUDIO_OUTPUT_FILE_RU
    intro_text_audio = INTRO_TEXT_AUDIO_OVERLAY_PATH_EN if language == "EN" else INTRO_TEXT_AUDIO_OVERLAY_PATH_RU
    tail_audio = TAIL_AUDIO_OUTPUT_FILE_EN if language == "EN" else TAIL_AUDIO_OUTPUT_FILE_RU
    tail_text_audio = TAIL_TEXT_AUDIO_OVERLAY_PATH_EN if language == "EN" else TAIL_TEXT_AUDIO_OVERLAY_PATH_RU
    main_audio = AUDIO_PATH_EN if language == "EN" else AUDIO_PATH_RU
    audio_with_tail = AUDIO_PATH_WITH_TAIL_EN if language == "EN" else AUDIO_PATH_WITH_TAIL_RU
    
    # Define output file paths
    if language == "EN" and orientation == "horizontal":
        intro_video = INTRO_VIDEO_EN_HORIZONTAL
        main_tail_video = VIDEO_EN_HORIZONTAL_MAIN_PLUS_TAIL
        final_video = FINAL_VIDEO_EN_HORIZONTAL
    elif language == "RU" and orientation == "horizontal":
        intro_video = INTRO_VIDEO_RU_HORIZONTAL
        main_tail_video = VIDEO_RU_HORIZONTAL_MAIN_PLUS_TAIL
        final_video = FINAL_VIDEO_RU_HORIZONTAL
    elif language == "EN" and orientation == "vertical":
        intro_video = INTRO_VIDEO_EN_VERTICAL
        main_tail_video = VIDEO_EN_VERTICAL_MAIN_PLUS_TAIL
        final_video = FINAL_VIDEO_EN_VERTICAL
    else:  # RU and vertical
        intro_video = INTRO_VIDEO_RU_VERTICAL
        main_tail_video = VIDEO_RU_VERTICAL_MAIN_PLUS_TAIL
        final_video = FINAL_VIDEO_RU_VERTICAL
    
    # Step 1: Create intro audio
    print(f"Creating intro audio for {language}...")
    CreateAudioFile(
        output_file=intro_audio,
        music_overlay_path=INTRO_MUSIC_OVERLAY_PATH,
        text_audio_overlay_path=intro_text_audio,
        set_duration_by_text_audio=True,
        time_of_music_before_voice=0.2,
        time_of_music_after_voice=1.5
    )
    
    # Step 2: Create intro video
    print(f"Creating intro video for {language} {orientation}...")
    CreateVideoFile(
        output_file=intro_video,
        size=size,
        resize_dim=resize_dim,
        audio_path=intro_audio,
        csv_path=INTRO_TEXT_OVERLAY_CSV_PATH,
        text_column=text_column,
        video_paths=INTRO_VIDEO_PATHS,
        use_audio_duration=False
    )
    
    # Step 3: Create tail audio
    print(f"Creating tail audio for {language}...")
    CreateAudioFile(
        output_file=tail_audio,
        music_overlay_path=TAIL_MUSIC_OVERLAY_PATH,
        text_audio_overlay_path=tail_text_audio,
        set_duration_by_text_audio=True,
        time_of_music_before_voice=2,
        time_of_music_after_voice=2
    )
    
    # Step 4: Combine main and tail audio
    print(f"Combining main and tail audio for {language}...")
    ConcatenateAudioFiles(
        audio_paths=[main_audio, tail_audio],
        output_file=audio_with_tail,
        silence_between=0.5
    )
    
    # Step 5: Create main+tail video
    print(f"Creating main+tail video for {language} {orientation}...")
    CreateVideoFile(
        output_file=main_tail_video,
        size=size,
        resize_dim=resize_dim,
        audio_path=audio_with_tail,
        csv_path=[CSV_PATH, TAIL_TEXT_OVERLAY_CSV_PATH],
        text_column=text_column,
        video_paths=VIDEO_PATHS + TAIL_VIDEO_PATHS,
        use_audio_duration=True
    )
    
    # Step 6: Concatenate intro with main+tail
    print(f"Creating final combined video for {language} {orientation}...")
    ConcatenateVideoFiles(
        video_paths=[intro_video, main_tail_video],
        output_file=final_video
    )
    
    print(f"✓ Completed {language} {orientation} video: {final_video}")


if __name__ == "__main__":
    # Create all four video variants
    create_complete_video_for_greece(language="EN", orientation="horizontal")
    create_complete_video_for_greece(language="RU", orientation="horizontal")
    create_complete_video_for_greece(language="EN", orientation="vertical")
    create_complete_video_for_greece(language="RU", orientation="vertical")

    # Or selectively create only specific variants:
    # create_complete_video(language="EN", orientation="horizontal")

