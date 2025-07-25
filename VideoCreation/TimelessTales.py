import os

from video_common import (
    load_video_overlay_entries_from_excel, 
    add_texts_to_image, 
    create_video_with_audio,
    VideoOverlayEntry,
    BASE_DIRECTORY
)
from video_common import add_text_to_image, add_voice_to_video, TextStyle, TextOverlay

# Define TimelessTales base directory
BASE_DIRECTORY_TT = os.path.join(BASE_DIRECTORY, "TT")

import os
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def resolve_path(path: str) -> str:
    """
    Resolves a path relative to BASE_DIRECTORY_TT to an absolute path.
    If the path is already absolute, returns it unchanged.
    
    Args:
        path: A relative or absolute file path
        
    Returns:
        str: An absolute file path
    """
    if not path:
        return ""
        
    # If path is already absolute, return it
    if os.path.isabs(path):
        return path
        
    # Otherwise join with BASE_DIRECTORY_TT
    return os.path.join(BASE_DIRECTORY_TT, path)

def load_tt_entries_from_excel(excel_path: str) -> List[VideoOverlayEntry]:
    """
    Load video overlay entries from an Excel file and convert relative paths
    to absolute paths using BASE_DIRECTORY_TT as the base.
    
    Args:
        excel_path: Path to the Excel file
        
    Returns:
        List of VideoOverlayEntry objects with resolved paths
    """
    entries = load_video_overlay_entries_from_excel(excel_path)
    resolved_entries = []
    
    for entry in entries:
        # Resolve paths to absolute paths if they're relative
        resolved_entry = VideoOverlayEntry(
            image_path=resolve_path(entry.image_path),
            audio_path=resolve_path(entry.audio_path),
            output_video_path=resolve_path(entry.output_video_path),
            overlays=entry.overlays,
            head_video_path=resolve_path(entry.head_video_path) if entry.head_video_path else "",
            tail_video_path=resolve_path(entry.tail_video_path) if entry.tail_video_path else "",
            status=entry.status,
            notes=entry.notes
        )
        resolved_entries.append(resolved_entry)
        logger.info(f"Resolved paths for entry: {resolved_entry.image_path}")
    
    return resolved_entries

def process_video_entries(csv_path: str) -> List[str]:
    """
    Process all video entries from the Excel file and create videos.
    
    Args:
        csv_path: Path to the CSV file containing video entries

    Returns:
        List of created video file paths
    """
    try:
        # Load entries from Excel with path resolution
        entries = load_tt_entries_from_excel(csv_path)
        created_videos = []

        for entry in entries:
            try:
                # Skip entries that don't have a status containing "ToDo" (case-insensitive, ignoring spaces)
                if not entry.status or not "todo" in entry.status.lower().replace(" ", ""):
                    logger.info(f"Skipping entry with status '{entry.status}': {entry.image_path}")
                    continue
                
                # Create image with text overlays
                image_clip, _ = add_texts_to_image(
                    image_path=entry.image_path,
                    text_overlays=entry.overlays,
                    write_image_as_file=False
                )

                if image_clip:
                    # Create video with audio
                    if entry.output_video_path:
                        # If output_video_path is specified, use the full path
                        video_path = create_video_with_audio(
                            image_clip=image_clip,
                            audio_path=entry.audio_path,
                            output_path=entry.output_video_path,
                            head_video_path=entry.head_video_path if entry.head_video_path else None,
                            tail_video_path=entry.tail_video_path if entry.tail_video_path else None
                        )
                    else:
                        # Otherwise use the default directory with auto-generated name
                        video_path = create_video_with_audio(
                            image_clip=image_clip,
                            audio_path=entry.audio_path,
                            output_dir=BASE_DIRECTORY_TT,
                            head_video_path=entry.head_video_path if entry.head_video_path else None,
                            tail_video_path=entry.tail_video_path if entry.tail_video_path else None
                        )
                    
                    if video_path:
                        created_videos.append(video_path)
                        logger.info(f"Successfully created video: {video_path}")
                    else:
                        logger.error(f"Failed to create video for entry with image: {entry.image_path}")
                else:
                    logger.error(f"Failed to create image clip for entry with image: {entry.image_path}")

            except Exception as e:
                logger.error(f"Error processing entry {entry.image_path}: {str(e)}")
                continue

        return created_videos

    except Exception as e:
        logger.error(f"Error loading entries from Excel: {str(e)}")
        return []

# if __name__ == "__main__":
#     csv_path = os.path.join(BASE_DIRECTORY_TT, "TimelessTales_Video_Tracker.xlsx")
#     created_videos = process_video_entries(csv_path)
    
#     if created_videos:
#         logger.info(f"Successfully created {len(created_videos)} videos")
#         for video in created_videos:
#             logger.info(f"Created: {video}")
#     else:
#         logger.error("No videos were created")













audio_path = resolve_path("Voice_Over_RU.mp3")


def test_image_text_overlay():
    # Test parameters
    image_path = resolve_path("Дама в розовом.png")
    
    textForTitle = "Дама в\nрозовом"
    horizontal_offsetForTitle = 30
    vertical_offsetForTitle = 35
    
    styleForTitle = TextStyle(
        font_size=90,
        text_color="black",
        stroke_color="black",
        stroke_width=0
    )

    textForAuthor = "Гребенщиков \nГеоргий Дмитриевич".upper()
    horizontal_offsetForAuthor = 30
    vertical_offsetForAuthor = 3
    
    styleForAuthor = TextStyle(
        font_size=30,
        text_color="black",
        stroke_color="black",
        stroke_width=0
    )

    # Process first layer of text (title)
    title_clip, title_path = add_text_to_image(
        image_path=image_path,
        text=textForTitle,
        horizontal_offset=horizontal_offsetForTitle,
        vertical_offset=vertical_offsetForTitle,
        style=styleForTitle,
        write_image_as_file=True
    )

    # Process second layer of text (author)
    if title_path:
        final_clip, final_path = add_text_to_image(
            image_path=title_path,
            text=textForAuthor,
            horizontal_offset=horizontal_offsetForAuthor,
            vertical_offset=vertical_offsetForAuthor,
            style=styleForAuthor,
            write_image_as_file=True
        )
        
        if final_path:
            print(f"Successfully created image: {final_path}")
            return final_clip  # Return the final composite clip for video creation
        else:
            print("Failed to add author text")
    else:
        print("Failed to add title text")
    
    return None

# if __name__ == "__main__":
#     result_clip = test_image_text_overlay()
#     if result_clip:
#         # Example with auto-generated filename
#         video_path = create_video_with_audio(
#             image_clip=result_clip, 
#             audio_path=audio_path, 
#             output_dir=BASE_DIRECTORY_TT,
#             head_video_path=None,  # No head video for this test
#             tail_video_path=None   # No tail video for this test
#         )
#         if video_path:
#             print(f"Successfully created video: {video_path}")
#         else:
#             print("Failed to create video")




def test_image_texts_overlay():
    # Test parameters
    image_path = resolve_path("Дама в розовом.png")
    
    # Create text overlays list
    text_overlays = [
        TextOverlay(
            text="Дама в\nрозовом",
            horizontal_offset=30,
            vertical_offset=35,
            style=TextStyle(
                font_size=90,
                text_color="black",
                stroke_color="black",
                stroke_width=0
            )
        ),
        TextOverlay(
            text="Гребенщиков \nГеоргий Дмитриевич".upper(),
            horizontal_offset=30,
            vertical_offset=3,
            style=TextStyle(
                font_size=30,
                text_color="black",
                stroke_color="black",
                stroke_width=0
            )
        )
    ]

    try:
        # Process all text overlays at once
        final_clip, final_path = add_texts_to_image(
            image_path=image_path,
            text_overlays=text_overlays,
            write_image_as_file=False  # Set to True if you want to save the final image
        )
        
        if final_clip:
            print(f"Successfully created image: {final_path}")
            return final_clip
        else:
            print("Failed to add texts to image")
            return None
    except Exception as e:
        print(f"Error creating image with text overlays: {e}")
        return None

# if __name__ == "__main__":
#     result_clip = test_image_texts_overlay()
#     if result_clip:
#         # Example with auto-generated filename
#         video_path = create_video_with_audio(
#             image_clip=result_clip, 
#             audio_path=audio_path, 
#             output_dir=BASE_DIRECTORY_TT,
#             head_video_path=None,  # No head video for this test
#             tail_video_path=None   # No tail video for this test
#         )
#         if video_path:
#             print(f"Successfully created video: {video_path}")
#         else:
#             print("Failed to create video")




# Uncomment to test
if __name__ == "__main__":

    # Intro
    # video_path = resolve_path(r"assets\intro\TT_INTRO.mp4")
    # voice_path = resolve_path(r"assets\intro\Welcome_RU_TT.mp3")
    # output_path = resolve_path(r"assets\intro\TT_INTRO_FINAL.mp4")
    
    # add_voice_to_video(video_path=video_path, voice_path=voice_path, output_path=output_path)

    # Tail
    video_path = resolve_path(r"assets\tail\TT_TAIL.mp4")
    voice_path = resolve_path(r"assets\tail\Tail_RU_TT.mp3")
    output_path = resolve_path(r"assets\tail\TT_TAIL_FINAL.mp4")
    
    add_voice_to_video(video_path=video_path, voice_path=voice_path, output_path=output_path)