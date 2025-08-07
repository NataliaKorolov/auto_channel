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
from datetime import datetime



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


        if image_clip.size != size:
            print(f"Resizing image clip from {image_clip.size} to {size}")
            image_clip = image_clip.resized(width=size[0], height=size[1])

        # Set image duration to match audio
        image_clip = image_clip.with_duration(audio.duration)
        
        # Add audio to clip
        main_clip = image_clip.with_audio(audio)
        dump_clip_info(main_clip, "Main clip before head video")
   
        # Add head video if provided
        head_clip = None
        if head_video_path:
            head_clip = prepare_video_clip(head_video_path, main_clip, "Head")
        
        # Add tail video if provided  
        tail_clip = None
        if tail_video_path:
            tail_clip = prepare_video_clip(tail_video_path, main_clip, "Tail")
        
        # Now you can concatenate using the prepared clips
        clips_to_concatenate = []
        
        if head_clip:
            clips_to_concatenate.append(head_clip)
            
        clips_to_concatenate.append(main_clip)
        
        if tail_clip:
            clips_to_concatenate.append(tail_clip)
        
        # Final concatenation
        if len(clips_to_concatenate) > 1:
            final_clip = concatenate_videoclips(clips_to_concatenate, method="compose")
        else:
            final_clip = main_clip
        
        # Final validation
        dump_clip_info(final_clip, "Final clip before writing")
        
        # Validate final clip before writing
        if final_clip is None:
            raise ValueError("Final clip is None - video composition failed")
            
        # Generate output path
        if output_path:
            # If a complete output path is provided, use it
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        else:
            # Generate output filename from audio name
            output_filename = f"{Path(audio_path).stem}.mp4"
            output_path = os.path.join(output_dir, output_filename)
        
        print(f"Writing video to: {output_path}")

        # In your video processing code:
        if head_clip and tail_clip:
            all_clips = [main_clip, head_clip, tail_clip, final_clip]
            all_names = ["Main", "Head", "Tail", "Final"]
            compare_clips_info(all_clips, all_names)        
        
        # Write video file with fps specified - Updated for MoviePy 2.2.1
        # YouTube-optimized export settings
        final_clip.write_videofile(
            output_path,
            fps=24,                    # Standard for YouTube
            codec="libx264",           # ✅ YouTube preferred
            audio_codec="aac",         # ✅ YouTube preferred
            preset="medium",           # Better quality than "fast"
            bitrate="8000k",          # 8 Mbps - good balance for 1080p
            audio_bitrate="128k",     # Standard audio quality
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            ffmpeg_params=[
                "-pix_fmt", "yuv420p",  # YouTube compatibility
                "-movflags", "+faststart"  # Web optimization
            ],
            threads=4,                # Use multiple threads for faster processing
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
            music_low = music_extended * 0.3  # Simple multiplication works best
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
        
        # Concatenate audio clips
        print("Concatenating audio clips...")
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

def add_voice_to_video(video_path: str, voice_path: str, output_path: str = None, output_dir: str = None) -> str:
    """
    Add voice audio to an existing video with music, placing the voice in the middle of the video timeline.
    
    Args:
        video_path: Path to the input video file
        voice_path: Path to the voice audio file
        output_path: Optional specific output path for the result video
        output_dir: Optional directory to save the result video (uses auto-generated filename)
        
    Returns:
        str: Path to the created video file, or None if failed
        
    Raises:
        ValueError: If voice audio is longer than video duration
    """
    try:
        
        # Load the video
        video_clip = VideoFileClip(video_path)
        
        # Load the voice audio
        voice_audio = AudioFileClip(voice_path)
        
        # Check if voice is longer than video
        if voice_audio.duration > video_clip.duration:
            video_clip.close()
            voice_audio.close()
            raise ValueError(f"Voice audio duration ({voice_audio.duration:.2f}s) is longer than video duration ({video_clip.duration:.2f}s)")
        
        # Calculate start time to center the voice
        start_time = (video_clip.duration - voice_audio.duration) / 2
        
        # Set the voice audio to start at the calculated time
        voice_audio = voice_audio.with_start(start_time)
        
        # Get the original video audio (music)
        original_audio = video_clip.audio
        
        # Composite the audio tracks (original music + voice)
        if original_audio:
            composite_audio = CompositeAudioClip([original_audio, voice_audio])
        else:
            # If video has no audio, just use the voice
            composite_audio = voice_audio
        
        # Set the composite audio to the video
        final_video = video_clip.with_audio(composite_audio)
        
        # Determine output path
        if output_path:
            result_path = output_path
        elif output_dir:
            # Generate filename based on input video name
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{video_name}_with_voice_{timestamp}.mp4"
            result_path = os.path.join(output_dir, filename)
        else:
            # Use same directory as input video
            video_dir = os.path.dirname(video_path)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{video_name}_with_voice_{timestamp}.mp4"
            result_path = os.path.join(video_dir, filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        
        # Write the final video
        final_video.write_videofile(
            result_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Clean up
        video_clip.close()
        voice_audio.close()
        final_video.close()
        if original_audio:
            original_audio.close()
        composite_audio.close()
        
        print(f"Successfully added voice to video: {result_path}")
        return result_path
        
    except Exception as e:
        print(f"Error adding voice to video: {str(e)}")
        # Clean up in case of error
        try:
            if 'video_clip' in locals():
                video_clip.close()
            if 'voice_audio' in locals():
                voice_audio.close()
            if 'final_video' in locals():
                final_video.close()
            if 'original_audio' in locals() and original_audio:
                original_audio.close()
            if 'composite_audio' in locals():
                composite_audio.close()
        except:
            pass
        return None

def dump_clip_info(clip, clip_name: str = "Clip") -> dict:
    """
    Dump comprehensive information about a MoviePy clip for debugging purposes.
    
    Args:
        clip: MoviePy clip object (VideoClip, AudioClip, CompositeVideoClip, etc.)
        clip_name: Name/identifier for the clip (for logging purposes)
        
    Returns:
        dict: Dictionary containing all available clip information
    """
    info = {
        "clip_name": clip_name,
        "clip_type": type(clip).__name__,
        "is_none": clip is None
    }
    
    if clip is None:
        print(f"{clip_name}: CLIP IS NONE!")
        return info
    
    try:
        # Basic properties
        info["has_duration"] = hasattr(clip, 'duration')
        if hasattr(clip, 'duration'):
            try:
                info["duration"] = clip.duration
                info["duration_valid"] = info["duration"] is not None and info["duration"] > 0
            except Exception as e:
                info["duration_error"] = str(e)
        
        # Video-specific properties
        if hasattr(clip, 'size'):
            try:
                info["size"] = clip.size
                info["width"] = clip.w if hasattr(clip, 'w') else None
                info["height"] = clip.h if hasattr(clip, 'h') else None
            except Exception as e:
                info["size_error"] = str(e)
        
        if hasattr(clip, 'fps'):
            try:
                info["fps"] = clip.fps
            except Exception as e:
                info["fps_error"] = str(e)
        
        # Audio properties
        if hasattr(clip, 'audio'):
            try:
                info["has_audio"] = clip.audio is not None
                if clip.audio:
                    info["audio_duration"] = getattr(clip.audio, 'duration', None)
            except Exception as e:
                info["audio_error"] = str(e)
        
        # Start and end times
        if hasattr(clip, 'start'):
            try:
                info["start"] = clip.start
            except Exception as e:
                info["start_error"] = str(e)
        
        if hasattr(clip, 'end'):
            try:
                info["end"] = clip.end
            except Exception as e:
                info["end_error"] = str(e)
        
        # Mask information
        if hasattr(clip, 'mask'):
            try:
                info["has_mask"] = clip.mask is not None
            except Exception as e:
                info["mask_error"] = str(e)
        
        # For CompositeVideoClip, get info about clips
        if hasattr(clip, 'clips'):
            try:
                info["num_clips"] = len(clip.clips) if clip.clips else 0
                info["clips_info"] = []
                if clip.clips:
                    for i, subclip in enumerate(clip.clips):
                        subinfo = {
                            "index": i,
                            "type": type(subclip).__name__,
                            "duration": getattr(subclip, 'duration', None),
                            "size": getattr(subclip, 'size', None),
                            "start": getattr(subclip, 'start', None)
                        }
                        info["clips_info"].append(subinfo)
            except Exception as e:
                info["clips_error"] = str(e)
        
        # Test if clip can generate frames
        if hasattr(clip, 'get_frame'):
            try:
                test_frame = clip.get_frame(0)
                info["can_get_frame"] = True
                info["frame_shape"] = test_frame.shape if hasattr(test_frame, 'shape') else None
            except Exception as e:
                info["can_get_frame"] = False
                info["get_frame_error"] = str(e)
        
        # Additional properties
        if hasattr(clip, 'filename'):
            info["filename"] = getattr(clip, 'filename', None)
        
        # Print summary
        print(f"\n=== {clip_name} Information ===")
        print(f"Type: {info['clip_type']}")
        
        if info.get('duration'):
            print(f"Duration: {info['duration']:.2f}s")
        elif 'duration_error' in info:
            print(f"Duration Error: {info['duration_error']}")
        
        if info.get('size'):
            print(f"Size: {info['size']} (W:{info.get('width')}, H:{info.get('height')})")
        elif 'size_error' in info:
            print(f"Size Error: {info['size_error']}")
        
        if info.get('fps'):
            print(f"FPS: {info['fps']}")
        
        if 'has_audio' in info:
            print(f"Has Audio: {info['has_audio']}")
            if info.get('audio_duration'):
                print(f"Audio Duration: {info['audio_duration']:.2f}s")
        
        if 'num_clips' in info:
            print(f"Number of subclips: {info['num_clips']}")
        
        if 'can_get_frame' in info:
            print(f"Can get frame: {info['can_get_frame']}")
            if info.get('frame_shape'):
                print(f"Frame shape: {info['frame_shape']}")
            elif 'get_frame_error' in info:
                print(f"Get frame error: {info['get_frame_error']}")
        
        # Print any errors
        errors = [k for k in info.keys() if k.endswith('_error')]
        if errors:
            print("Errors found:")
            for error_key in errors:
                print(f"  {error_key}: {info[error_key]}")
        
        print("=" * (len(clip_name) + 20))
        
    except Exception as e:
        info["general_error"] = str(e)
        print(f"Error analyzing {clip_name}: {str(e)}")
    
    return info


def prepare_video_clip(video_path: str, main_clip, clip_name: str = "Video") -> Optional[VideoFileClip]:
    """
    Load a video clip from path and adjust its parameters to match the main clip.
    No concatenation is performed - just preparation.
    
    Args:
        video_path: Path to the video file to load
        main_clip: The reference clip to match parameters against
        clip_name: Name for logging purposes
        
    Returns:
        VideoFileClip: The prepared video clip with matching parameters, or None if failed
    """
    if not video_path or not os.path.exists(video_path):
        if video_path:
            print(f"Warning: {clip_name} video not found: {video_path}")
        return None
    
    video_clip = None
    try:
        print(f"Loading {clip_name.lower()} video: {video_path}")
        
        # Load the video
        video_clip = VideoFileClip(video_path)
        
        # Validate the clip can generate frames
        try:
            test_frame = video_clip.get_frame(0)
            print(f"✅ {clip_name} video can generate frames: {test_frame.shape}")
        except Exception as e:
            print(f"❌ {clip_name} video cannot generate frames: {e}")
            video_clip.close()
            return None
        
        # Dump original clip info
        dump_clip_info(video_clip, f"{clip_name} video (original)")
        
        # Adjust dimensions to match main clip
        if video_clip.w != main_clip.w or video_clip.h != main_clip.h:
            print(f"Resizing {clip_name.lower()} video from {video_clip.size} to {main_clip.size}")
            video_clip = video_clip.resized(width=main_clip.w, height=main_clip.h)
            
            # Validate after resizing
            try:
                test_frame = video_clip.get_frame(0)
                print(f"✅ {clip_name} video can generate frames after resize: {test_frame.shape}")
            except Exception as e:
                print(f"❌ {clip_name} video cannot generate frames after resize: {e}")
                video_clip.close()
                return None
        else:
            print(f"✅ {clip_name} video dimensions already match main clip")
        
        # Dump final clip info
        dump_clip_info(video_clip, f"{clip_name} video (prepared)")
        
        print(f"✅ Successfully prepared {clip_name.lower()} video")
        return video_clip
        
    except Exception as e:
        print(f"❌ Error preparing {clip_name.lower()} video: {e}")
        if video_clip:
            video_clip.close()
        return None
    

def compare_clips_info(clips: List, clip_names: List[str]) -> dict:
    """
    Compare comprehensive information between multiple MoviePy clips and highlight differences.
    
    Args:
        clips: List of MoviePy clip objects to compare
        clip_names: List of names/identifiers for the clips (must match length of clips)
        
    Returns:
        dict: Dictionary containing comparison results and differences
    """
    
    if len(clips) != len(clip_names):
        raise ValueError(f"Number of clips ({len(clips)}) must match number of names ({len(clip_names)})")
    
    if len(clips) < 2:
        raise ValueError("At least 2 clips are required for comparison")
    
    # Get info for all clips
    all_info = []
    for clip, name in zip(clips, clip_names):
        info = dump_clip_info(clip, name)
        all_info.append(info)
    
    comparison = {
        "clip_names": clip_names,
        "individual_info": all_info,
        "differences": {},
        "similarities": {},
        "warnings": []
    }
    
    # Define properties to compare
    properties_to_compare = [
        'clip_type', 'is_none', 'duration', 'duration_valid', 'size', 'width', 'height', 
        'fps', 'has_audio', 'audio_duration', 'start', 'end', 'has_mask', 'num_clips',
        'can_get_frame', 'frame_shape'
    ]
    
    print(f"\n{'='*80}")
    print(f"COMPARING {len(clips)} CLIPS: {' vs '.join(clip_names)}")
    print(f"{'='*80}")
    
    for prop in properties_to_compare:
        values = [info.get(prop) for info in all_info]
        
        # Check if all values are the same
        if all(val == values[0] for val in values):
            comparison["similarities"][prop] = values[0]
        else:
            comparison["differences"][prop] = dict(zip(clip_names, values))
            
            # Print differences
            print(f"\n🔍 DIFFERENCE in {prop}:")
            for name, val in zip(clip_names, values):
                print(f"   {name}: {val}")
    
    # Special comparisons and warnings
    print(f"\n{'='*50}")
    print("DETAILED ANALYSIS")
    print(f"{'='*50}")
    
    # Check for None clips
    none_clips = [name for info, name in zip(all_info, clip_names) if info.get('is_none')]
    if none_clips:
        warning = f"⚠️  WARNING: These clips are None: {', '.join(none_clips)}"
        comparison["warnings"].append(warning)
        print(warning)
    
    # Duration comparison
    durations = []
    for info, name in zip(all_info, clip_names):
        if info.get('duration') is not None:
            durations.append((name, info['duration']))
    
    if len(durations) > 1:
        print(f"\n📏 Duration Analysis:")
        durations.sort(key=lambda x: x[1])
        shortest = durations[0]
        longest = durations[-1]
        
        print(f"   Shortest: {shortest[0]} = {shortest[1]:.2f}s")
        print(f"   Longest:  {longest[0]} = {longest[1]:.2f}s")
        
        if longest[1] - shortest[1] > 0.1:  # More than 0.1 second difference
            warning = f"Duration mismatch: {longest[1] - shortest[1]:.2f}s difference"
            comparison["warnings"].append(warning)
            print(f"   ⚠️  {warning}")
        
        # Show all durations if more than 3 clips
        if len(durations) > 3:
            print(f"   All durations:")
            for name, duration in durations:
                print(f"     {name}: {duration:.2f}s")
    
    # Size comparison
    sizes = []
    for info, name in zip(all_info, clip_names):
        if info.get('size') is not None:
            sizes.append((name, info['size']))
    
    
    # Audio comparison
    audio_info = []
    for info, name in zip(all_info, clip_names):
        has_audio = info.get('has_audio', False)
        audio_duration = info.get('audio_duration')
        audio_info.append((name, has_audio, audio_duration))
    
    print(f"\n🔊 Audio Analysis:")
    for name, has_audio, audio_duration in audio_info:
        if has_audio:
            duration_str = f" ({audio_duration:.2f}s)" if audio_duration else " (unknown duration)"
            print(f"   {name}: Has audio{duration_str}")
        else:
            print(f"   {name}: No audio")
    
    # Check for audio mismatches
    audio_states = [info[1] for info in audio_info]  # has_audio values
    if not all(state == audio_states[0] for state in audio_states):
        warning = "Audio presence mismatch between clips"
        comparison["warnings"].append(warning)
        print(f"   ⚠️  {warning}")
    
    # Frame generation capability
    frame_capabilities = []
    for info, name in zip(all_info, clip_names):
        can_get_frame = info.get('can_get_frame')
        get_frame_error = info.get('get_frame_error')
        frame_capabilities.append((name, can_get_frame, get_frame_error))
    
    print(f"\n🎬 Frame Generation Analysis:")
    for name, can_get, error in frame_capabilities:
        if can_get is True:
            print(f"   {name}: ✅ Can generate frames")
        elif can_get is False:
            print(f"   {name}: ❌ Cannot generate frames - {error}")
        else:
            print(f"   {name}: ❓ Frame generation untested")
    
    # Check for frame generation issues
    failed_clips = [name for name, can_get, _ in frame_capabilities if can_get is False]
    if failed_clips:
        warning = f"Frame generation failed for: {', '.join(failed_clips)}"
        comparison["warnings"].append(warning)
        print(f"   ⚠️  {warning}")
    
    # Composite clip analysis
    composite_clips = []
    for info, name in zip(all_info, clip_names):
        if info.get('num_clips') is not None:
            composite_clips.append((name, info['num_clips'], info.get('clips_info', [])))
    
    if composite_clips:
        print(f"\n🎭 Composite Clip Analysis:")
        for name, num_clips, clips_info in composite_clips:
            print(f"   {name}: {num_clips} subclips")
            if clips_info:
                for i, subclip_info in enumerate(clips_info[:3]):  # Show first 3 subclips
                    print(f"     [{i}] {subclip_info.get('type', 'Unknown')} - "
                          f"Duration: {subclip_info.get('duration', 'N/A')}")
                if len(clips_info) > 3:
                    print(f"     ... and {len(clips_info) - 3} more subclips")
    
    # Error summary
    all_errors = []
    for info, name in zip(all_info, clip_names):
        errors = [k for k in info.keys() if k.endswith('_error')]
        if errors:
            all_errors.extend([(name, k, info[k]) for k in errors])
    
    if all_errors:
        print(f"\n❌ Error Summary:")
        for name, error_type, error_msg in all_errors:
            print(f"   {name} - {error_type}: {error_msg}")
            comparison["warnings"].append(f"{name} has {error_type}: {error_msg}")
    
    # Final summary
    print(f"\n{'='*50}")
    print("COMPARISON SUMMARY")
    print(f"{'='*50}")
    print(f"Clips compared: {len(clips)}")
    print(f"Properties compared: {len(properties_to_compare)}")
    print(f"Similarities found: {len(comparison['similarities'])}")
    print(f"Differences found: {len(comparison['differences'])}")
    print(f"Warnings generated: {len(comparison['warnings'])}")
    
    if comparison['warnings']:
        print(f"\n⚠️  CRITICAL ISSUES:")
        for warning in comparison['warnings']:
            print(f"   • {warning}")
    else:
        print(f"\n✅ No critical issues found!")
    
    print(f"{'='*80}")
    
    return comparison    