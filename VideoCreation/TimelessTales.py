from video_common import (
    load_video_overlay_entries_from_excel, 
    add_texts_to_image, 
    create_video_with_audio,
    VideoOverlayEntry
)
from video_common import add_text_to_image, TextStyle, TextOverlay

import os
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_video_entries(csv_path: str) -> List[str]:
    """
    Process all video entries from the Excel file and create videos.
    
    Args:
        csv_path: Path to the CSV file containing video entries

    Returns:
        List of created video file paths
    """
    try:
        # Load entries from Excel
        entries = load_video_overlay_entries_from_excel(csv_path)
        created_videos = []

        for entry in entries:
            try:
                # Create image with text overlays
                image_clip, _ = add_texts_to_image(
                    image_path=entry.image_path,
                    text_overlays=entry.overlays,
                    write_image_as_file=False
                )

                if image_clip:
                    # Create video with audio
                    video_path = create_video_with_audio(
                        image_clip=image_clip,
                        audio_path=entry.audio_path,
                        output_dir=os.path.dirname(entry.output_video_path)
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

if __name__ == "__main__":
    csv_path = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot\TT\TimelessTales_Video_Tracker.xlsx"
    created_videos = process_video_entries(csv_path)
    
    if created_videos:
        logger.info(f"Successfully created {len(created_videos)} videos")
        for video in created_videos:
            logger.info(f"Created: {video}")
    else:
        logger.error("No videos were created")













audio_path = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot\TT\Voice_Over_RU.mp3" 


def test_image_text_overlay():
    # Test parameters
    image_path = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot\TT\Дама в розовом.png"
    
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
#         video_path = create_video_with_audio(result_clip, audio_path)
#         if video_path:
#             print(f"Successfully created video: {video_path}")
#         else:
#             print("Failed to create video")




def test_image_texts_overlay():
    # # Test parameters
    image_path = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot\TT\Дама в розовом.png"
    
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

# if __name__ == "__main__":
#     result_clip = test_image_texts_overlay()
#     if result_clip:
#         video_path = create_video_with_audio(result_clip, audio_path)
#         if video_path:
#             print(f"Successfully created video: {video_path}")
#         else:
#             print("Failed to create video")