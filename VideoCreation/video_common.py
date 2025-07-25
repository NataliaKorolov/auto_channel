import os
import pandas as pd  # Add this import for Excel support
from typing import List, Tuple, Optional, Dict, Any, Union
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import TextClip, ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips, CompositeAudioClip
from moviepy import concatenate_videoclips
from dataclasses import dataclass, field
from pathlib import Path
from PIL import Image
import re  # Add this import at the top with other imports
import cv2  # Add for GetVideoInfo function



# Base directory constants
BASE_DIRECTORY = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot"

DEFAULT_FONT = "DejaVuSans"

MIN_DURATION = 1  # seconds


def get_texts_from_csv(csv_paths: Union[str, List[str]], column: str) -> List[str]:
    """
    Read texts from a specified column in one or multiple CSV or Excel files.
    
    Args:
        csv_paths: Path to a single file or a list of file paths
        column: Column name containing the text data
        
    Returns:
        Combined list of texts from all files
    """
    result = []
    
    # Convert single path to list for uniform handling
    if isinstance(csv_paths, str):
        paths_to_process = [csv_paths]
    else:
        paths_to_process = csv_paths
    
    # Process each file
    for csv_path in paths_to_process:
        try:
            # Check file extension to determine how to read
            if csv_path.lower().endswith('.xlsx') or csv_path.lower().endswith('.xls'):
                df = pd.read_excel(csv_path, engine='openpyxl')
                print(f"Reading Excel file: {csv_path}")
            else:
                df = pd.read_csv(csv_path)
                print(f"Reading CSV file: {csv_path}")
                
            # Check if column exists
            if column not in df.columns:
                print(f"Warning: Column '{column}' not found in {csv_path}")
                continue
                
            # Add texts from this file to results
            file_texts = df[column].fillna("").tolist()
            result.extend(file_texts)
            print(f"Added {len(file_texts)} texts from {csv_path}")
            
        except Exception as e:
            print(f"Error reading file {csv_path} or column '{column}': {e}")
    
    print(f"Total texts collected: {len(result)}")
    return result

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


def CreateAudioFile(
    output_file: str,
    music_overlay_path: str, 
    text_audio_overlay_path: str,
    set_duration_by_text_audio: bool = True,
    time_of_music_after_voice: float = 0.0,
    time_of_music_before_voice: float = 0.0
) -> None:
    """
    Create and export an audio file by combining music and text audio tracks.
    The final duration is determined by the longer of the two input audio files,
    or by text audio duration + music timing parameters if set_duration_by_text_audio is True.

    Args:
        output_file: Full path for the output audio file
        music_overlay_path: Full path to background music file
        text_audio_overlay_path: Full path to text audio file
        set_duration_by_text_audio: If True, set duration to text audio + music timing parameters
        time_of_music_after_voice: Time in seconds for music to last after the voice
        time_of_music_before_voice: Time in seconds for music to play before the voice starts
    """
    music_audio = None
    text_audio = None
    composite_audio = None

    try:
        # Load audio files and check durations
        if os.path.exists(music_overlay_path):
            music_audio = AudioFileClip(music_overlay_path)
            print(f"Music audio duration: {music_audio.duration:.2f}s")
        else:
            print(f"Warning: Music file not found: {music_overlay_path}")

        if os.path.exists(text_audio_overlay_path):
            text_audio = AudioFileClip(text_audio_overlay_path)
            print(f"Text audio duration: {text_audio.duration:.2f}s")
        else:
            print(f"Warning: Text audio file not found: {text_audio_overlay_path}")

        # Check if we have at least one audio file
        if not music_audio and not text_audio:
            print("Error: No valid audio files found")
            return

        # Determine final duration
        if set_duration_by_text_audio and text_audio:
            final_duration = time_of_music_before_voice + text_audio.duration + time_of_music_after_voice
            print(f"Final audio duration: {final_duration:.2f}s ({time_of_music_before_voice}s intro + {text_audio.duration:.2f}s text + {time_of_music_after_voice}s outro)")
        else:
            if music_audio and text_audio:
                final_duration = max(music_audio.duration, text_audio.duration)
                print(f"Final audio duration: {final_duration:.2f}s (max of both tracks)")
            elif music_audio:
                final_duration = music_audio.duration
                print(f"Final audio duration: {final_duration:.2f}s (music only)")
            elif text_audio:
                final_duration = text_audio.duration
                print(f"Final audio duration: {final_duration:.2f}s (text only)")
            else:
                print("Error: No valid audio files found")
                return

        # Prepare audio tracks for mixing
        audio_tracks = []

        # Handle text audio - now with delayed start
        if text_audio:
            if time_of_music_before_voice > 0:
                # Create text audio that starts after the specified delay
                text_to_use = text_audio.with_start(time_of_music_before_voice)
                print(f"Set text audio to start at {time_of_music_before_voice:.2f}s")
            else:
                text_to_use = text_audio
            
            audio_tracks.append(text_to_use)
            print("Added text audio track")

        # Handle music audio
        if music_audio:
            if music_audio.duration < final_duration:
                print(f"Warning: Music duration ({music_audio.duration:.2f}s) is shorter than required final duration ({final_duration:.2f}s). Music will be looped.")
                # Loop music to cover the full duration
                loops_needed = int(final_duration / music_audio.duration) + 1
                music_looped = concatenate_audioclips([music_audio] * loops_needed)
                music_extended = music_looped.subclipped(0, final_duration)
            else:
                # Trim to final duration
                music_extended = music_audio.subclipped(0, final_duration)

            # Reduce music volume to 30%
            music_low = music_extended  # .volumex(0.3)
            audio_tracks.append(music_low)
            print("Added background music track (30% volume)")

        # Create composite audio
        if len(audio_tracks) > 1:
            composite_audio = CompositeAudioClip(audio_tracks)
            print("Created composite audio with multiple tracks")
        else:
            composite_audio = audio_tracks[0]
            print("Using single audio track")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Export audio file
        print(f"Exporting audio to: {output_file}")
        composite_audio.write_audiofile(output_file)

        print(f"Successfully created audio file: {output_file}")

    except Exception as e:
        print(f"Error creating audio file: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up resources
        try:
            if music_audio and hasattr(music_audio, 'close'):
                music_audio.close()
            if text_audio and hasattr(text_audio, 'close'):
                text_audio.close()
            if composite_audio and hasattr(composite_audio, 'close'):
                composite_audio.close()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")



def CreateVideoFile(output_file: str, size: Tuple[int, int], resize_dim: str, audio_path: str, csv_path: str, text_column: str, video_paths: List[str], use_audio_duration: bool = False) -> None:
    """Create and export a video with overlaid text and audio.
    
    Args:
        output_file: Path for the output video file
        size: Video dimensions (width, height)
        resize_dim: Resize dimension ("width" or "height")
        audio_path: Path to the audio file
        csv_path: Path to the CSV file with texts
        text_column: Column name for text overlay
        video_paths: List of video file paths
        use_audio_duration: If True, adjust video duration to match audio duration
    """
    texts = get_texts_from_csv(csv_path, text_column)
    clips = []
    for idx, path in enumerate(video_paths):
        if not os.path.exists(path):
            print(f"Warning: {path} not found. Skipping.")
            continue
        try:
            clip = VideoFileClip(path)
            clip = resize_and_crop_clip(clip, size, resize_dim)
            if idx < len(texts):
                clip = add_text_overlay(clip, texts[idx], size)
            else:
                print(f"Warning: No text for clip {idx+1}")
            clips.append(clip)
        except Exception as e:
            print(f"Error processing {path}: {e}")

    if not clips:
        print("No video clips found. Exiting.")
        return

    # Get audio duration first if we need to match it
    audio_duration = None
    if use_audio_duration:
        try:
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            audio_clip.close()
            print(f"Audio duration: {audio_duration:.2f}s")
        except Exception as e:
            print(f"Error reading audio file: {e}")
            use_audio_duration = False

    # Create initial video from clips
    final_clip = concatenate_videoclips(clips, method="compose")
    video_duration = final_clip.duration
    print(f"Initial video duration: {video_duration:.2f}s")

    # Adjust video duration to match audio if flag is set
    if use_audio_duration and audio_duration:
        if audio_duration < video_duration:
            # Shorten video to match audio
            print(f"Shortening video from {video_duration:.2f}s to {audio_duration:.2f}s")
            final_clip = final_clip.with_duration(audio_duration)
        elif audio_duration > video_duration:
            # Extend video by repeating the last clip
            print(f"Extending video from {video_duration:.2f}s to {audio_duration:.2f}s")
            time_needed = audio_duration - video_duration
            
            if clips:  # Make sure we have clips
                last_clip = clips[-1]
                last_clip_duration = last_clip.duration
                
                # Calculate how many times we need to repeat the last clip
                repeats_needed = int(time_needed / last_clip_duration) + 1
                additional_clips = [last_clip] * repeats_needed
                
                # Create extended clip list
                extended_clips = clips + additional_clips
                final_clip = concatenate_videoclips(extended_clips, method="compose")
                
                # Trim to exact audio duration
                final_clip = final_clip.with_duration(audio_duration)
                print(f"Added {repeats_needed} repetitions of last clip")
        
        video_duration = final_clip.duration

    if video_duration < MIN_DURATION:
        print(f"Warning: Final video duration ({video_duration:.2f}s) is shorter than MIN_DURATION ({MIN_DURATION}s).")
    else:
        print(f"Final video duration: {video_duration:.2f}s")

    try:
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        if audio_duration > video_duration:
            print(f"Warning: Audio duration ({audio_duration:.2f}s) is longer than video duration ({video_duration:.2f}s). Audio will be cut to video length.")
            audio_clip = audio_clip.with_duration(video_duration)
        final_with_audio = final_clip.with_audio(audio_clip)
        final_with_audio.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            bitrate="20000k",
            audio_fps=44100,
            logger=None,
            threads=4
        )
    except Exception as e:
        print(f"Error exporting video: {e}")


def ConcatenateVideoFiles(
    video_paths: List[str],
    output_file: str,
    check_compatibility: bool = True
) -> bool:
    """
    Concatenate multiple video files into a single video.
    
    Args:
        video_paths: List of paths to video files to concatenate
        output_file: Path for the output concatenated video
        check_compatibility: Whether to check size compatibility (default: True)
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        ValueError: If videos have incompatible sizes
        FileNotFoundError: If any video file doesn't exist
    """
    
    if not video_paths:
        raise ValueError("No video paths provided")
    
    # Check if all files exist
    for path in video_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video file not found: {path}")
    
    video_clips = []
    reference_size = None
    
    try:
        # Load video clips and check compatibility
        for i, path in enumerate(video_paths):
            print(f"Loading video {i+1}/{len(video_paths)}: {os.path.basename(path)}")
            
            # Get video info using OpenCV for quick size check
            if check_compatibility:
                cap = cv2.VideoCapture(path)
                if not cap.isOpened():
                    raise ValueError(f"Cannot open video file: {path}")
                
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                current_size = (width, height)
                cap.release()
                
                if reference_size is None:
                    reference_size = current_size
                    print(f"Reference size set to: {reference_size}")
                elif current_size != reference_size:
                    error_msg = (
                        f"Size mismatch detected!\n"
                        f"Reference size: {reference_size}\n"
                        f"File '{os.path.basename(path)}' size: {current_size}\n"
                        f"All videos must have the same dimensions for concatenation."
                    )
                    raise ValueError(error_msg)
            
            # Load with MoviePy
            clip = VideoFileClip(path)
            video_clips.append(clip)
            print(f"Loaded: {os.path.basename(path)} - Duration: {clip.duration:.2f}s")
        
        # Concatenate videos
        print("Concatenating videos...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Write output
        print(f"Writing concatenated video to: {output_file}")
        final_video.write_videofile(
            output_file,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        total_duration = sum(clip.duration for clip in video_clips)
        print(f"Successfully concatenated {len(video_paths)} videos")
        print(f"Total duration: {total_duration:.2f}s")
        print(f"Output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error during concatenation: {str(e)}")
        return False
        
    finally:
        # Clean up clips
        for clip in video_clips:
            if clip:
                clip.close()

def GetVideoInfo(video_path: str) -> Optional[dict]:
    """
    Get basic information about a video file.
    
    Args:
        video_path: Path to the video file
    
    Returns:
        dict: Video information including size, duration, fps
        None: If video cannot be read
    """
    if not os.path.exists(video_path):
        return None
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'width': width,
            'height': height,
            'size': (width, height),
            'fps': fps,
            'frame_count': frame_count,
            'duration': duration,
            'filename': os.path.basename(video_path)
        }
        
    except Exception as e:
        print(f"Error getting video info for {video_path}: {str(e)}")
        return None

def ConcatenateAudioFiles(
    audio_paths: List[str],
    output_file: str,
    silence_between: float = 0
) -> bool:
    """
    Concatenate multiple audio files into a single audio file.
    
    Args:
        audio_paths: List of paths to audio files to concatenate
        output_file: Path for the output concatenated audio
        crossfade_duration: Duration of crossfade between clips in seconds (default: 0)
        volume_adjustments: Dictionary mapping clip index to volume multiplier (default: None)
        add_fade_in: Duration of fade in effect for the first clip in seconds (default: 0)
        add_fade_out: Duration of fade out effect for the last clip in seconds (default: 0)
        silence_between: Duration of silence to insert between clips in seconds (default: 0)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not audio_paths:
        print("No audio paths provided")
        return False
    
    audio_clips = []
    
    try:
        # Load all audio clips
        for i, path in enumerate(audio_paths):
            if not os.path.exists(path):
                print(f"Warning: Audio file not found: {path}")
                continue
                
            print(f"Loading audio {i+1}/{len(audio_paths)}: {os.path.basename(path)}")
            clip = AudioFileClip(path)
            
            # Add to clip list
            audio_clips.append(clip)
            
        if not audio_clips:
            print("No valid audio clips found")
            return False
            
        # # Apply fade in to first clip if requested
        # if add_fade_in > 0 and audio_clips:
        #     audio_clips[0] = audio_clips[0].fadein(add_fade_in)
        #     print(f"Added {add_fade_in}s fade in to first clip")
            
        # # Apply fade out to last clip if requested
        # if add_fade_out > 0 and audio_clips:
        #     audio_clips[-1] = audio_clips[-1].fadeout(add_fade_out)
        #     print(f"Added {add_fade_out}s fade out to last clip")
        
        # Insert silence between clips if requested
        if silence_between > 0 and len(audio_clips) > 1:
            from moviepy.audio.AudioClip import AudioClip
            silence = AudioClip(lambda t: 0, duration=silence_between)
            clips_with_silence = []
            
            for i, clip in enumerate(audio_clips):
                clips_with_silence.append(clip)
                if i < len(audio_clips) - 1:  # Don't add silence after last clip
                    clips_with_silence.append(silence)
                    
            audio_clips = clips_with_silence
            print(f"Inserted {silence_between}s silence between clips")
        
        # Concatenate audio clips with or without crossfade
        print("Concatenating audio clips...")
        # if crossfade_duration > 0:
        #     final_audio = concatenate_audioclips(audio_clips, crossfade_duration)
        #     print(f"Applied {crossfade_duration}s crossfade between clips")
        # else:
        final_audio = concatenate_audioclips(audio_clips)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write the final audio to file
        print(f"Writing concatenated audio to: {output_file}")
        final_audio.write_audiofile(output_file)
        
        total_duration = sum(clip.duration for clip in audio_clips)
        print(f"Successfully concatenated {len(audio_clips)} audio clips")
        print(f"Total duration: {total_duration:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"Error during audio concatenation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up clips
        for clip in audio_clips:
            try:
                clip.close()
            except:
                pass