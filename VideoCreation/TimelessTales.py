import os

from video_common import (
    load_video_overlay_entries_from_excel, 
    create_video_from_image_and_audio,
    resolve_path,
    VideoOverlayEntry,
    BASE_DIRECTORY
)


# Define TimelessTales base directory
BASE_DIRECTORY_TT = os.path.join(BASE_DIRECTORY, "TT")

from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            image_path=resolve_path(entry.image_path, BASE_DIRECTORY_TT),
            audio_path=resolve_path(entry.audio_path, BASE_DIRECTORY_TT),
            output_video_path=resolve_path(entry.output_video_path, BASE_DIRECTORY_TT),
            overlays=entry.overlays,
            head_video_path=resolve_path(entry.head_video_path, BASE_DIRECTORY_TT) if entry.head_video_path else "",
            tail_video_path=resolve_path(entry.tail_video_path, BASE_DIRECTORY_TT) if entry.tail_video_path else "",
            status=entry.status,
            notes=entry.notes
        )
        resolved_entries.append(resolved_entry)
        logger.info(f"Resolved paths for entry: {resolved_entry.image_path}")
    
    return resolved_entries

def process_video_entries(csv_path: str, use_temp_dir: bool = False) -> List[str]:
    """Process all video entries with the new combined function"""
    try:
        entries = load_tt_entries_from_excel(csv_path)
        created_videos = []

        for entry in entries: 
            try:
                # Skip non-todo entries
                if not entry.status or not "todo" in entry.status.lower().replace(" ", ""):
                    logger.info(f"Skipping entry with status '{entry.status}': {entry.image_path}")
                    continue
                
                logger.info(f"Processing entry: {os.path.basename(entry.image_path)}")
                
                # Validate files exist
                if not os.path.exists(entry.image_path):
                    logger.error(f"Image file not found: {entry.image_path}")
                    continue
                    
                if not os.path.exists(entry.audio_path):
                    logger.error(f"Audio file not found: {entry.audio_path}")
                    continue
                
                # 🚀 ONE-STEP PROCESS: Create complete video
                logger.info("Creating complete video...")
                video_path = create_video_from_image_and_audio(
                    image_path=entry.image_path,
                    text_overlays=entry.overlays,
                    audio_path=entry.audio_path,
                    output_path=entry.output_video_path if entry.output_video_path else None,
                    output_dir=BASE_DIRECTORY_TT if not entry.output_video_path else None,
                    head_video_path=entry.head_video_path or None,
                    tail_video_path=entry.tail_video_path or None,
                    use_temp_dir=use_temp_dir
                )
                
                if video_path:
                    created_videos.append(video_path)
                    logger.info(f"✅ Successfully created video: {os.path.basename(video_path)}")
                else:
                    logger.error(f"❌ Failed to create video for entry: {entry.image_path}")

            except Exception as e:
                logger.error(f"❌ Error processing entry {entry.image_path}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        logger.info(f"Completed processing. Created {len(created_videos)} videos out of {len(entries)} entries.")
        return created_videos

    except Exception as e:
        logger.error(f"Error loading entries from Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    csv_path = os.path.join(BASE_DIRECTORY_TT, "TEST_TimelessTales_Video_Tracker.xlsx")
    created_videos = process_video_entries(csv_path)
    
    if created_videos:
        logger.info(f"Successfully created {len(created_videos)} videos")
        for video in created_videos:
            logger.info(f"Created: {video}")
    else:
        logger.error("No videos were created")




