import pandas as pd
from typing import List, Tuple, Optional
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import TextClip, ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip  # Add this import
from moviepy import concatenate_videoclips
from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image
import re
from pathlib import Path
import os

# Base directory constants
BASE_DIRECTORY = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot"

DEFAULT_FONT = "DejaVuSans"

def get_texts_from_csv(csv_path: str, column: str) -> List[str]:
    """Read texts from a specified column in a CSV file."""
    try:
        df = pd.read_csv(csv_path)
        return df[column].fillna("").tolist()
    except Exception as e:
        print(f"Error reading CSV or column '{column}': {e}")
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

@dataclass
class TextStyle:
    font: str = "DejaVuSans"
    font_size: int = 50
    text_color: str = "black"
    stroke_color: str = "white"
    stroke_width: int = 2

def add_text_to_image(
    image_path: str, 
    text: str, 
    horizontal_offset: int, 
    vertical_offset: int, 
    style: TextStyle = TextStyle(),
    output_dir: str = BASE_DIRECTORY,
    write_image_as_file: bool = False
) -> Tuple[CompositeVideoClip, str]:
    """
    Add text to an image with specified positioning and style.
    
    Args:
        image_path: Path to the input image
        text: Text to overlay on the image
        horizontal_offset: Percentage from left (1-100)
        vertical_offset: Percentage from bottom (1-100)
        style: TextStyle configuration
        output_dir: Directory for output file
        write_image_as_file: Whether to save the image to disk
        
    Returns:
        Tuple containing:
        - CompositeVideoClip: The processed image as a clip
        - str: Path to the saved image (empty string if not saved)
    """
    try:
        # Validate inputs
        if not os.path.exists(image_path):
            raise ValueError(f"Image path does not exist: {image_path}")
        if not (1 <= horizontal_offset <= 100 and 1 <= vertical_offset <= 100):
            raise ValueError("Offset values must be between 1 and 100")

        # Create output filename
        output_path = ""
        if write_image_as_file:
            text_cleaned = re.sub(r'[\\/*?:"<>|\n]', '_', text).replace(' ', '_')
            output_filename = f"{Path(image_path).stem}_{text_cleaned}{Path(image_path).suffix}"
            output_path = os.path.join(output_dir, output_filename)

        # Load image
        img = Image.open(image_path)
        
        # Create text clip
        txt_clip = TextClip(
            text=text,
            font=style.font,
            font_size=style.font_size,
            color=style.text_color,
            stroke_color=style.stroke_color,
            stroke_width=style.stroke_width,
            method='caption',
            size=(int(img.width * 0.8), None),  # limit width to 80% of image
            text_align = "center",
            margin=(10, 10, 10, 10)
        )

        # Calculate position with extra spacing
        x_pos = int((img.width * horizontal_offset) / 100) - txt_clip.w // 2
        y_pos = int(img.height * (100 - vertical_offset) / 100) - txt_clip.h - 20
        
        # Create composite
        result = CompositeVideoClip([
            ImageClip(image_path),
            txt_clip.with_position((x_pos, y_pos))
        ])
        
        # Save result if requested
        if write_image_as_file:
            result.save_frame(output_path)
        
        return result, output_path

    except Exception as e:
        print(f"Error processing image: {e}")
        return None, ""


@dataclass
class TextOverlay:
    text: str
    horizontal_offset: int  # Percentage from left (1-100)
    vertical_offset: int    # Percentage from bottom (1-100)
    style: TextStyle = field(default_factory=TextStyle)


def add_texts_to_image(
    image_path: str,
    text_overlays: List[TextOverlay],
    output_dir: str = BASE_DIRECTORY,
    write_image_as_file: bool = False
) -> Tuple[CompositeVideoClip, str]:
    """
    Add multiple text overlays to an image with specified positioning and styles.
    
    Args:
        image_path: Path to the input image
        text_overlays: List of TextOverlay objects containing text and positioning info
        output_dir: Directory for output file
        write_image_as_file: Whether to save the image to disk
        
    Returns:
        Tuple containing:
        - CompositeVideoClip: The processed image as a clip
        - str: Path to the saved image (empty string if not saved)
    """
    try:
        # Validate inputs
        if not os.path.exists(image_path):
            raise ValueError(f"Image path does not exist: {image_path}")
        
        for overlay in text_overlays:
            if not (1 <= overlay.horizontal_offset <= 100 and 1 <= overlay.vertical_offset <= 100):
                raise ValueError("Offset values must be between 1 and 100")

        # Create output filename
        output_path = ""
        if write_image_as_file:
            # Use first text for filename
            text_cleaned = re.sub(r'[\\/*?:"<>|\n]', '_', text_overlays[0].text).replace(' ', '_')
            output_filename = f"{Path(image_path).stem}_{text_cleaned}{Path(image_path).suffix}"
            output_path = os.path.join(output_dir, output_filename)

        # Load image
        img = Image.open(image_path)
        
        # Create base clip
        clips = [ImageClip(image_path)]
        
        # Add each text overlay
        for overlay in text_overlays:
            txt_clip = TextClip(
                text=overlay.text,
                font=overlay.style.font,
                font_size=overlay.style.font_size,
                color=overlay.style.text_color,
                stroke_color=overlay.style.stroke_color,
                stroke_width=overlay.style.stroke_width,
                method='caption',
                size=(int(img.width * 0.8), None),  # limit width to 80% of image
                text_align="center",
                margin=(10, 10, 10, 10)
            )

            # Calculate position with extra spacing
            x_pos = int((img.width * overlay.horizontal_offset) / 100) - txt_clip.w // 2
            y_pos = int(img.height * (100 - overlay.vertical_offset) / 100) - txt_clip.h - 20
            
            clips.append(txt_clip.with_position((x_pos, y_pos)))
        
        # Create composite
        result = CompositeVideoClip(clips)
        
        # Save result if requested
        if write_image_as_file:
            result.save_frame(output_path)
        
        return result, output_path

    except Exception as e:
        print(f"Error processing image: {e}")
        return None, ""

def add_head_video(main_clip, head_video_path: str):
    """
    Prepends a head video to the beginning of the main clip.
    
    Args:
        main_clip: The main video clip
        head_video_path: Path to the video to prepend
        
    Returns:
        A new clip with the head video prepended
    """
    if not head_video_path or not os.path.exists(head_video_path):
        if head_video_path:
            print(f"Warning: Head video not found: {head_video_path}")
        return main_clip
    
    head_clip = None    
    try:
        # Load the head video
        head_clip = VideoFileClip(head_video_path)
        
        # Ensure head video has the same dimensions as the main clip
        if head_clip.size != main_clip.size:
            print(f"Resizing head video from {head_clip.size} to {main_clip.size}")
            head_clip = head_clip.resized(width=main_clip.w, height=main_clip.h)
        
        # Prepend the head clip to the main clip
        result_clip = concatenate_videoclips([head_clip, main_clip], method="compose")
        print(f"Successfully prepended head video: {head_video_path}")
        
        return result_clip
        
    except Exception as e:
        print(f"Error prepending head video: {e}")
        return main_clip
    finally:
        # Ensure proper cleanup even if an exception occurs
        if head_clip is not None:
            try:
                head_clip.close()
            except Exception as e:
                print(f"Warning: Error closing head clip: {e}")


def add_tail_video(main_clip, tail_video_path: str):
    """
    Appends a tail video to the end of the main clip.
    
    Args:
        main_clip: The main video clip
        tail_video_path: Path to the video to append
        
    Returns:
        A new clip with the tail video appended
    """
    if not tail_video_path or not os.path.exists(tail_video_path):
        if tail_video_path:
            print(f"Warning: Tail video not found: {tail_video_path}")
        return main_clip
    
    tail_clip = None    
    try:
        # Load the tail video
        tail_clip = VideoFileClip(tail_video_path)
        
        # Ensure tail video has the same dimensions as the main clip
        if tail_clip.size != main_clip.size:
            print(f"Resizing tail video from {tail_clip.size} to {main_clip.size}")
            tail_clip = tail_clip.resized(width=main_clip.w, height=main_clip.h)
        
        # Append the tail clip to the main clip
        result_clip = concatenate_videoclips([main_clip, tail_clip], method="compose")
        print(f"Successfully appended tail video: {tail_video_path}")
        
        return result_clip
        
    except Exception as e:
        print(f"Error appending tail video: {e}")
        return main_clip
    finally:
        # Ensure proper cleanup even if an exception occurs
        if tail_clip is not None:
            try:
                tail_clip.close()
            except Exception as e:
                print(f"Warning: Error closing tail clip: {e}")

def create_video_with_audio(
    image_clip: CompositeVideoClip, 
    audio_path: str,
    output_dir: str = BASE_DIRECTORY,
    output_path: str = None,
    head_video_path: str = None,
    tail_video_path: str = None,
    size: Tuple[int, int] = (1920, 1080)
) -> str:
    """
    Create a video from an image clip with audio.
    
    Args:
        image_clip: The image as a CompositeVideoClip
        audio_path: Path to the audio file
        output_dir: Directory to save the video (used if output_path is not provided)
        output_path: Full path for output file (takes precedence over output_dir)
        head_video_path: Optional path to video to prepend to the beginning
        tail_video_path: Optional path to video to append to the end
        size: Output video dimensions (width, height)
        
    Returns:
        Path to the created video file, or empty string on error
    """
    audio = None
    main_clip = None
    final_clip = None
        
    try:
        # Load audio
        audio = AudioFileClip(audio_path)
        
        # Verify we have a valid image clip
        if image_clip is None:
            raise ValueError("Invalid image clip provided")
            
        # Set image duration to match audio
        image_clip = image_clip.with_duration(audio.duration)
        
        # Add audio to clip
        main_clip = image_clip.with_audio(audio)
        
        # Add head video if provided
        if head_video_path:
            main_clip = add_head_video(main_clip, head_video_path)
            
        # Add tail video if provided
        if tail_video_path:
            final_clip = add_tail_video(main_clip, tail_video_path)
        else:
            final_clip = main_clip
            
        # Generate output path
        if output_path:
            # If a complete output path is provided, use it
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        else:
            # Generate output filename from audio name
            output_filename = f"{Path(audio_path).stem}.mp4"
            output_path = os.path.join(output_dir, output_filename)
        
        # Write video file with fps specified - REMOVED verbose and logger parameters
        final_clip.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            audio_fps=44100
        )
        
        return output_path

    except Exception as e:
        print(f"Error creating video: {e}")
        return ""
    finally:
        # Clean up resources in reverse order of creation
        try:
            # Close clips only if they exist and are not references to other clips
            if final_clip is not None and final_clip is not main_clip:
                try:
                    final_clip.close()
                except Exception as e:
                    pass
            
            if main_clip is not None and main_clip is not image_clip:
                try:
                    main_clip.close()
                except Exception as e:
                    pass
                
            if audio is not None:
                try:
                    audio.close()
                except Exception as e:
                    pass
                
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")



@dataclass
class VideoOverlayEntry:
    image_path: str  # Path to the input image (absolute or relative to BASE_DIRECTORY_TT)
    audio_path: str  # Path to the audio file (absolute or relative to BASE_DIRECTORY_TT)
    output_video_path: str  # Path for the output video (absolute or relative to BASE_DIRECTORY_TT)
    overlays: List[TextOverlay]  # List of text overlays to apply
    head_video_path: Optional[str] = ""  # Path to video to prepend (absolute or relative to BASE_DIRECTORY_TT)
    tail_video_path: Optional[str] = ""  # Path to video to append (absolute or relative to BASE_DIRECTORY_TT)
    status: Optional[str] = ""  # Status of the entry (e.g., "ToDo")
    notes: Optional[str] = ""  # Additional notes

def parse_video_overlay_entry(row: pd.Series) -> VideoOverlayEntry:
    """
    Parse a row from Excel/CSV into a VideoOverlayEntry.
    Handles empty cells and type conversions safely.
    """
    overlays = []
    i = 1
    
    def safe_int_convert(value, default: int) -> int:
        """Safely convert a value to integer with a default fallback"""
        if pd.isna(value) or value == '':
            return default
        try:
            return int(float(str(value)))  # Handle both string and float inputs
        except (ValueError, TypeError):
            print(f"Warning: Could not convert '{value}' to integer, using default: {default}")
            return default

    def safe_str_convert(value, default: str) -> str:
        """Safely convert a value to string with a default fallback"""
        if pd.isna(value) or value == '':
            return default
        return str(value).strip()

    while f"Text {i}" in row:
        text = safe_str_convert(row.get(f"Text {i}"), "")
        
        # Skip if text is empty
        if not text:
            break
            
        try:
            overlay = TextOverlay(
                text=text,
                horizontal_offset=safe_int_convert(row.get(f"Hor Offset {i}"), 50),  # Default to center
                vertical_offset=safe_int_convert(row.get(f"Vert Offset {i}"), 50),  # Default to middle
                style=TextStyle(
                    font_size=safe_int_convert(row.get(f"Font Size {i}"), 50),      # Default size
                    text_color=safe_str_convert(row.get(f"Color {i}"), "black"),    # Default color
                    stroke_color=safe_str_convert(row.get(f"Stroke Color {i}"), "white"),  # Default stroke
                    stroke_width=safe_int_convert(row.get(f"Stroke Width {i}"), 2)  # Default width
                )
            )
            overlays.append(overlay)
            print(f"Successfully parsed overlay {i}: {overlay.text}")
        except Exception as e:
            print(f"Warning: Error parsing overlay {i}: {str(e)}")
            break
        i += 1

    # Ensure we have at least one overlay
    if not overlays:
        raise ValueError("No valid text overlays found in row")

    return VideoOverlayEntry(
        image_path=safe_str_convert(row["Image Path"], ""),
        audio_path=safe_str_convert(row["Audio Path"], ""),
        output_video_path=safe_str_convert(row["Output Video Path"], ""),
        overlays=overlays,
        head_video_path=safe_str_convert(row.get("Head Video", ""), ""),
        tail_video_path=safe_str_convert(row.get("Tail Video", ""), ""),
        status=safe_str_convert(row.get("Status"), ""),
        notes=safe_str_convert(row.get("Notes"), "")
    )

def load_video_overlay_entries_from_csv(csv_path: str) -> List[VideoOverlayEntry]:
    """
    Load video overlay entries from a CSV file with UTF-8 encoding support.
    Supports both local CSV files and CSV files exported from Google Sheets.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of VideoOverlayEntry objects
    """
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        return [parse_video_overlay_entry(row) for _, row in df.iterrows()]
    except UnicodeDecodeError:
        # If UTF-8 fails, try with cp1251 (Windows Cyrillic encoding)
        df = pd.read_csv(csv_path, encoding='cp1251')
        return [parse_video_overlay_entry(row) for _, row in df.iterrows()]

def load_video_overlay_entries_from_gsheet(sheet_url: str) -> List[VideoOverlayEntry]:
    """
    Load video overlay entries directly from a Google Sheet.
    
    Args:
        sheet_url: The sharing URL of your Google Sheet
        
    Returns:
        List of VideoOverlayEntry objects
    """
    # Convert Google Sheets URL to CSV export URL
    if 'spreadsheets/d/' in sheet_url:
        sheet_id = sheet_url.split('spreadsheets/d/')[1].split('/')[0]
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    else:
        raise ValueError("Invalid Google Sheets URL")
    
    # Google Sheets exports in UTF-8
    df = pd.read_csv(csv_url, encoding='utf-8')
    return [parse_video_overlay_entry(row) for _, row in df.iterrows()]

def load_video_overlay_entries_from_excel(excel_path: str) -> List[VideoOverlayEntry]:
    """
    Load video overlay entries from an Excel file with UTF-8 encoding support.
    
    Args:
        excel_path: Path to the Excel file
        
    Returns:
        List of VideoOverlayEntry objects
    """ 
    try:
        # Try reading with openpyxl engine which handles encoding better
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        # Convert any NaN values to empty strings to avoid parsing errors
        df = df.fillna('')
        
        # Parse each row into a VideoOverlayEntry
        entries = []
        for _, row in df.iterrows():
            try:
                entry = parse_video_overlay_entry(row)
                entries.append(entry)
            except Exception as e:
                print(f"Error parsing row: {str(e)}")
                continue
                
        return entries
        
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return []



