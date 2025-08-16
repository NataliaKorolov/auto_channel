import os
import pandas as pd  # Add this import for Excel support
from typing import List, Tuple, Optional, Union
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
import traceback
from datetime import datetime

import subprocess
import tempfile

# Add import for the new image processing function
from image_common import create_image_with_text_overlays_static

# Base directory constants
BASE_DIRECTORY = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot"

DEFAULT_FONT = "DejaVuSans"

MIN_DURATION = 1  # seconds

# Utility dataclasses and functions

@dataclass
class TextStyle:
    font: str = "DejaVuSans"
    font_size: int = 50
    text_color: str = "black"
    stroke_color: str = "white"
    stroke_width: int = 2

@dataclass
class TextOverlay:
    text: str
    horizontal_offset: int  # Percentage from left (1-100)
    vertical_offset: int    # Percentage from bottom (1-100)
    style: TextStyle = field(default_factory=TextStyle)

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

def get_texts_from_csv(csv_paths: Union[str, List[str]], column: str) -> List[str]:
    """
    Read texts from a specified column in one or multiple CSV or Excel files.
    """
    result = []
    if isinstance(csv_paths, str):
        paths_to_process = [csv_paths]
    else:
        paths_to_process = csv_paths
    
    for csv_path in paths_to_process:
        # Validate file exists before attempting to read
        if not os.path.exists(csv_path):
            print(f"Warning: File not found: {csv_path}")
            continue
            
        df = None
        try:
            print(f"Reading file: {csv_path}")
            
            if csv_path.lower().endswith('.xlsx') or csv_path.lower().endswith('.xls'):
                df = pd.read_excel(csv_path, engine='openpyxl')
            else:
                df = pd.read_csv(csv_path)
            
            if column not in df.columns:
                print(f"Warning: Column '{column}' not found in {csv_path}")
                print(f"Available columns: {list(df.columns)}")
                continue
                
            file_texts = df[column].fillna("").tolist()
            result.extend(file_texts)
            print(f"Successfully read {len(file_texts)} texts from {csv_path}")
            
        except Exception as e:
            print(f"Error reading file {csv_path} or column '{column}': {e}")
            traceback.print_exc()
        finally:
            # Clean up DataFrame resources
            if df is not None:
                try:
                    del df
                except:
                    pass
    
    print(f"Total texts loaded: {len(result)}")
    return result


def add_text_overlay(clip: VideoFileClip, text: str, size: Tuple[int, int]) -> CompositeVideoClip:
    """Overlay centered text on a video clip."""
    txt_clip = None
    positioned_txt = None
    
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
        positioned_txt = txt_clip.with_position(position)
        
        return CompositeVideoClip([clip, positioned_txt], size=size).with_duration(clip.duration)
        
    except Exception as e:
        print(f"Error creating text overlay: {e}")
        
        # Clean up on error
        if positioned_txt:
            try:
                positioned_txt.close()
            except:
                pass
        if txt_clip:
            try:
                txt_clip.close()
            except:
                pass
        
        # Return original clip on error
        return CompositeVideoClip([clip], size=size).with_duration(clip.duration)
        
    except Exception as e:
        print(f"Error creating text overlay: {e}")
        # Clean up on error
        if positioned_txt:
            try:
                positioned_txt.close()
            except:
                pass
        if txt_clip:
            try:
                txt_clip.close()
            except:
                pass
        return clip


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
    original_clip = None  # Keep reference to original for cleanup
    
    try:
        print(f"Loading {clip_name.lower()} video: {video_path}")
        
        # Load the video
        video_clip = VideoFileClip(video_path)
        original_clip = video_clip  # Keep reference for potential cleanup
        
        # Validate the clip can generate frames
        try:
            test_frame = video_clip.get_frame(0)
            print(f"✅ {clip_name} video can generate frames: {test_frame.shape}")
        except Exception as e:
            print(f"❌ {clip_name} video cannot generate frames: {e}")
            video_clip.close()
            return None
        
         
        # Adjust dimensions to match main clip
        if video_clip.w != main_clip.w or video_clip.h != main_clip.h:
            print(f"Resizing {clip_name.lower()} video from {video_clip.size} to {main_clip.size}")
            
            # Create resized clip
            resized_clip = video_clip.resized(width=main_clip.w, height=main_clip.h)
            
            # Validate resized clip before switching references
            try:
                test_frame = resized_clip.get_frame(0)
                print(f"✅ {clip_name} video can generate frames after resize: {test_frame.shape}")
                
                # Only close original and switch if resize was successful
                original_clip.close()
                video_clip = resized_clip
                original_clip = video_clip  # Update reference
                
            except Exception as e:
                print(f"❌ {clip_name} video cannot generate frames after resize: {e}")
                # Clean up both clips on resize failure
                try:
                    resized_clip.close()
                except:
                    pass
                try:
                    original_clip.close()
                except:
                    pass
                return None
        else:
            print(f"✅ {clip_name} video dimensions already match main clip")
        
    
        print(f"✅ Successfully prepared {clip_name.lower()} video")
        return video_clip
        
    except Exception as e:
        print(f"❌ Error preparing {clip_name.lower()} video: {e}")
        
        # Clean up any clips that were created
        if video_clip is not None:
            try:
                video_clip.close()
            except Exception as cleanup_error:
                print(f"Warning: Error closing video_clip during cleanup: {cleanup_error}")
                
        # If original_clip is different from video_clip, close it too
        if original_clip is not None and original_clip is not video_clip:
            try:
                original_clip.close()
            except Exception as cleanup_error:
                print(f"Warning: Error closing original_clip during cleanup: {cleanup_error}")
                
        return None



def get_youtube_optimized_settings(silent: bool = False) -> dict:
    """Get optimized settings for YouTube upload"""
    return {
        "fps": 12,
        "codec": "libx264",
        "audio_codec": "aac",
        "preset": "slow",
        "bitrate": "1500k",
        "audio_bitrate": "128k",
        "temp_audiofile": "temp-audio.m4a",
        "remove_temp": True,
        "ffmpeg_params": [
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-crf", "23",
            "-tune", "stillimage",
            "-g", "120",
            "-keyint_min", "12",
            "-profile:v", "high",
            "-level", "4.0",
            "-maxrate", "2250k",
            "-bufsize", "4500k",
            "-colorspace", "bt709",
            "-color_primaries", "bt709",
            "-color_trc", "bt709"
        ],
        "threads": 4,
        "logger": None if silent else "bar"  # 🚀 FIXED: Configurable logger
    }


def create_video_from_image_and_audio(
    image_path: str,
    text_overlays: List[TextOverlay],
    audio_path: str,
    output_path: str = None,
    output_dir: str = BASE_DIRECTORY,
    head_video_path: str = None,
    tail_video_path: str = None,
    size: Tuple[int, int] = (1920, 1080),
    use_ffmpeg_concat: bool = True,
    use_temp_dir: bool = False,
    safe_area_pct: Tuple[int, int, int, int] = (5, 6, 14, 6),
    max_text_width_ratio: float = 0.90
) -> str:
    """
    Complete pipeline: Create video from image + text overlays + audio with optional head/tail.
    Now uses the new PIL-based static image overlay function for better performance.
    
    Returns:
        str: Path to created video file, or empty string on error
    """
    # Initialize all clips for proper cleanup tracking
    audio = None
    image_clip = None
    main_clip = None
    final_clip = None
    temp_files = []
    temp_dir = None
    
    try:
        print(f"🎬 Creating video from image and audio...")
        print(f"📁 Image: {os.path.basename(image_path)}")
        print(f"🎵 Audio: {os.path.basename(audio_path)}")
        
        # Validate inputs
        if not os.path.exists(image_path):
            raise ValueError(f"Image file not found: {image_path}")
        if not os.path.exists(audio_path):
            raise ValueError(f"Audio file not found: {audio_path}")
        
        # 🚀 FIX: Ensure output_dir has a valid value
        if output_dir is None:
            output_dir = BASE_DIRECTORY
        
        # Setup temporary directory if requested
        if use_temp_dir:
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="video_creation_")
            print(f"📁 Using temporary directory: {temp_dir}")
        
        # STEP 1: Create static image with text overlays using PIL
        print("🎨 Creating image with text overlays (using PIL)...")
        
        # Determine temporary output directory for the overlay image
        overlay_output_dir = temp_dir if use_temp_dir else os.path.join(output_dir, "temp_overlays")
        
        overlay_image_path = create_image_with_text_overlays_static(
            image_path=image_path,
            text_overlays=text_overlays,
            output_dir=overlay_output_dir,
            safe_area_pct=safe_area_pct,
            max_text_width_ratio=max_text_width_ratio
        )
        
        if not overlay_image_path or not os.path.exists(overlay_image_path):
            raise ValueError("Failed to create image with text overlays")
        
        # Track temporary file for cleanup
        if use_temp_dir:
            temp_files.append(overlay_image_path)
        
        print(f"✅ Created overlay image: {os.path.basename(overlay_image_path)}")
        
        # STEP 2: Load audio and create video clip from the overlay image
        print("🎵 Loading audio...")
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        print(f"⏱️ Audio duration: {audio_duration:.2f} seconds")
        
        print("🖼️ Creating video clip from overlay image...")
        image_clip = ImageClip(overlay_image_path, duration=audio_duration)
        
        # Resize image clip to target size
        print(f"📐 Resizing to {size[0]}x{size[1]}...")
        image_clip = image_clip.resized(size)
        
        # Set audio
        main_clip = image_clip.with_audio(audio)
        print(f"✅ Main video clip created: {audio_duration:.2f}s at {size[0]}x{size[1]}")
        
        # STEP 3: Handle head and tail videos
        clips_to_concat = []
        
        # Add head video if provided
        if head_video_path and os.path.exists(head_video_path):
            print(f"🎬 Adding head video: {os.path.basename(head_video_path)}")
            head_clip = prepare_video_clip(head_video_path, main_clip, "Head")
            if head_clip:
                clips_to_concat.append(head_clip)
        
        # Add main clip
        clips_to_concat.append(main_clip)
        
        # Add tail video if provided
        if tail_video_path and os.path.exists(tail_video_path):
            print(f"🎬 Adding tail video: {os.path.basename(tail_video_path)}")
            tail_clip = prepare_video_clip(tail_video_path, main_clip, "Tail")
            if tail_clip:
                clips_to_concat.append(tail_clip)
        
        # STEP 4: Concatenate clips if needed
        if len(clips_to_concat) > 1:
            print(f"🔗 Concatenating {len(clips_to_concat)} clips...")
            final_clip = concatenate_videoclips(clips_to_concat, method="compose")
        else:
            final_clip = clips_to_concat[0]
        
        # STEP 5: Generate output path and export
        if not output_path:
            # Generate filename from image name
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_filename = f"{base_name}_video.mp4"
            output_path = os.path.join(output_dir, output_filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"💾 Exporting final video: {os.path.basename(output_path)}")
        print(f"⏱️ Final duration: {final_clip.duration:.2f} seconds")
        
        # Get optimized export settings
        export_settings = get_youtube_optimized_settings(silent=False)
        
        # Export the video
        final_clip.write_videofile(
            output_path,
            **export_settings
        )
        
        print(f"✅ Video created successfully: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        import traceback
        traceback.print_exc()
        return ""
        
    finally:
        # Clean up all clips
        clips_to_cleanup = [audio, image_clip, main_clip, final_clip]
        for clip in clips_to_cleanup:
            if clip:
                try:
                    clip.close()
                except:
                    pass
        
        # Clean up temporary files if using temp directory
        if use_temp_dir and temp_files:
            print("🧹 Cleaning up temporary files...")
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        print(f"🗑️ Removed: {os.path.basename(temp_file)}")
                except Exception as e:
                    print(f"⚠️ Could not remove temp file {temp_file}: {e}")
        
        # Clean up temporary directory
        if use_temp_dir and temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                print(f"🗑️ Removed temporary directory: {temp_dir}")
            except Exception as e:
                print(f"⚠️ Could not remove temp directory {temp_dir}: {e}")

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
    music_extended = None
    music_looped = None
    text_to_use = None

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

        # ✅ CORRECT for MoviePy 2.2.1:
        music_extended = music_extended * 0.3  # Simple multiplication works best
        
        audio_tracks.append(music_extended)
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
        traceback.print_exc()

    finally:
        # Clean up resources in proper order
        print("Cleaning up audio creation resources...")
        
        cleanup_items = [
            ("composite_audio", composite_audio),
            ("music_extended", music_extended),
            ("music_looped", music_looped),
            ("text_to_use", text_to_use),
            ("text_audio", text_audio),
            ("music_audio", music_audio)
        ]
        
        for name, item in cleanup_items:
            if item is not None:
                try:
                    print(f"Closing {name}")
                    item.close()
                except Exception as cleanup_error:
                    print(f"Warning: Error closing {name}: {cleanup_error}")




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

def CreateVideoFile(
    output_file: str, 
    size: Tuple[int, int], 
    resize_dim: str, 
    audio_path: str, 
    csv_path: str, 
    text_column: str, 
    video_paths: List[str], 
    use_audio_duration: bool = False
) -> None:
    """Create and export a video with overlaid text and audio."""
    clips = []
    final_clip = None
    audio_clip = None
    final_with_audio = None
    audio_duration = 0  # Initialize audio_duration
    
    try:
        texts = get_texts_from_csv(csv_path, text_column)
        
        # Load audio first to get duration
        if os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            print(f"Audio duration: {audio_duration:.2f}s")
        else:
            print(f"Warning: Audio file not found: {audio_path}")
            return
        
        for idx, path in enumerate(video_paths):
            if not os.path.exists(path):
                print(f"Warning: {path} not found. Skipping.")
                continue
                
            original_clip = None
            current_clip = None
            
            try:
                print(f"Loading video {idx+1}: {os.path.basename(path)}")
                
                # ✅ ADDED: Test if video can be loaded
                original_clip = VideoFileClip(path)

                current_clip = original_clip
                 
                resized_clip = current_clip.resized(size)
                
                # # Resize the clip
                # resized_clip = resize_and_crop_clip(current_clip, size, resize_dim)
                
                try:
                    resized_clip.get_frame(0)
                    print(f"✓ Resized clip is valid: {os.path.basename(path)}")
                except Exception as frame_error:
                    print(f"❌ CORRUPTED RESIZED CLIP: {os.path.basename(path)} - {frame_error}")
                    # Clean up corrupted resized clip
                    if resized_clip is not current_clip:
                        try:
                            resized_clip.close()
                        except:
                            pass
                    if current_clip:
                        try:
                            current_clip.close()
                        except:
                            pass
                    continue  # Skip this corrupted file

                # ✅ FIXED: Use identity check instead of equality
                if resized_clip is not current_clip:
                    # current_clip.close()
                    current_clip = resized_clip
                
                # Add text overlay if available
                if idx < len(texts) and texts[idx].strip():
                    text_overlay_clip = add_text_overlay(current_clip, texts[idx, size])
                    
                    text_overlay_clip.get_frame(0)
                    
                    # ✅ FIXED: Use identity check and validate result
                    if text_overlay_clip is not None and text_overlay_clip is not current_clip:
                        # current_clip.close()
                        current_clip = text_overlay_clip
                    elif text_overlay_clip is None:
                        print(f"⚠️ Warning: text overlay failed for clip {idx+1}, using original clip")
                
                # ✅ ADDED: Final validation before adding to clips list
                if current_clip is None:
                    print(f"❌ ERROR: current_clip is None for {path}")
                    continue
                    
                try:
                    # Test that the clip can generate frames
                    test_frame = current_clip.get_frame(0)
                    # Test that the clip has valid duration
                    test_duration = current_clip.duration
                    if test_duration <= 0:
                        print(f"❌ ERROR: Invalid duration ({test_duration}) for {path}")
                        current_clip.close()
                        continue
                        
                    clips.append(current_clip)
                    print(f"✅ Successfully processed clip {idx+1}: {os.path.basename(path)} (duration: {test_duration:.2f}s)")
                    
                except Exception as validation_error:
                    print(f"❌ ERROR: Final validation failed for {path}: {validation_error}")
                    if current_clip:
                        current_clip.close()
                    continue
                
            except Exception as e:
                print(f"❌ Error processing {path}: {e}")
                # Clean up on error
                if current_clip and current_clip is not original_clip:
                    try:
                        current_clip.close()
                    except:
                        pass
                if original_clip:
                    try:
                        original_clip.close()
                    except:
                        pass
                continue  # Skip this file and continue with others

        if not clips:
            print("❌ No valid video clips found after processing. Cannot create video.")
            print(f"📊 Processing summary:")
            print(f"   - Total video files: {len(video_paths)}")
            print(f"   - Files found: {sum(1 for path in video_paths if os.path.exists(path))}")
            print(f"   - Valid clips created: {len(clips)}")
            return

        # Create initial video from clips
        print(f"Creating final video from {len(clips)} valid clips...")
        
        # ✅ ADDED: Debug clip information before concatenation
        for i, clip in enumerate(clips):
            try:
                print(f"Clip {i+1}: duration={clip.duration:.2f}s, size={clip.size}")
            except Exception as e:
                print(f"Clip {i+1}: ERROR getting info - {e}")
        
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # ✅ ADDED: Validate final_clip before proceeding
        if final_clip is None:
            print("❌ ERROR: concatenate_videoclips returned None")
            print("This usually means all input clips were invalid or incompatible")
            return
            
        try:
            video_duration = final_clip.duration
            print(f"Initial video duration: {video_duration:.2f}s")
        except Exception as duration_error:
            print(f"❌ ERROR: Cannot get duration from final_clip: {duration_error}")
            return

        # Adjust video duration to match audio if flag is set
        if use_audio_duration and audio_duration:
            if audio_duration < video_duration:
                # Shorten video to match audio
                print(f"Shortening video from {video_duration:.2f}s to {audio_duration:.2f}s")
                shortened_clip = final_clip.with_duration(audio_duration)
                final_clip.close()
                final_clip = shortened_clip
                
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
                    extended_final = concatenate_videoclips(extended_clips, method="compose")
                    
                    # ✅ ADDED: Validate extended_final before proceeding
                    if extended_final is None:
                        print("❌ ERROR: Extended concatenate_videoclips returned None")
                        return
                    
                    # Close old final_clip
                    final_clip.close()
                    final_clip = extended_final
                    
                    # Trim to exact audio duration
                    trimmed_clip = final_clip.with_duration(audio_duration)
                    final_clip.close()
                    final_clip = trimmed_clip
                    print(f"Added {repeats_needed} repetitions of last clip")
            
            video_duration = final_clip.duration

        if video_duration < MIN_DURATION:
            print(f"Warning: Final video duration ({video_duration:.2f}s) is shorter than MIN_DURATION ({MIN_DURATION}s).")
        else:
            print(f"Final video duration: {video_duration:.2f}s")

        # Apply audio to video (audio was already loaded at the beginning)
        if audio_duration > video_duration:
            print(f"Warning: Audio duration ({audio_duration:.2f}s) is longer than video duration ({video_duration:.2f}s). Audio will be cut to video length.")
            trimmed_audio = audio_clip.with_duration(video_duration)
            audio_clip.close()
            audio_clip = trimmed_audio

        # ✅ ADDED: Test if final_clip can generate frames BEFORE creating final_with_audio
        try:
            test_frame = final_clip.get_frame(0)
            print(f"✓ final_clip is valid and can generate frames: {test_frame.shape}")
        except Exception as frame_error:
            print(f"❌ CORRUPTED final_clip - cannot generate frames: {frame_error}")
            return
            
        final_with_audio = final_clip.with_audio(audio_clip)
        
        # ✅ ADDED: Validate final_with_audio before proceeding
        if final_with_audio is None:
            print("❌ ERROR: with_audio() returned None")
            return
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # ✅ ADDED: Test if final_with_audio can generate frames
        try:
            test_frame = final_with_audio.get_frame(0)
            print(f"✓ final_with_audio is valid and can generate frames: {test_frame.shape}")
        except Exception as frame_error:
            print(f"❌ CORRUPTED final_with_audio - cannot generate frames: {frame_error}")
            return

        # Write video
        final_with_audio.write_videofile(
            output_file,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",        # 🚀 FASTEST preset (was "medium")
            bitrate="3000k",          # 🚀 LOWER bitrate (was "8000k") 
            audio_bitrate="64k",      # 🚀 LOWER audio quality (was "128k")
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
             ffmpeg_params=[
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-crf", "28",             # 🚀 HIGHER compression = faster
                "-tune", "fastdecode"     # 🚀 OPTIMIZE for speed
            ],
            threads=4,
            logger=None               # 🚀 DISABLE verbose logging
        )
        
        print(f"Successfully created video: {output_file}")
        
    except Exception as e:
        print(f"Error creating video: {e}")
        traceback.print_exc()
        
    finally:
        # Clean up all resources
        print("Cleaning up CreateVideoFile resources...")
        
        # Clean up clips in reverse order
        if final_with_audio:
            try:
                final_with_audio.close()
            except Exception as e:
                print(f"Warning: Error closing final_with_audio: {e}")
                
        if audio_clip:
            try:
                audio_clip.close()
            except Exception as e:
                print(f"Warning: Error closing audio_clip: {e}")
                
        if final_clip:
            try:
                final_clip.close()
            except Exception as e:
                print(f"Warning: Error closing final_clip: {e}")
                
        # Clean up individual clips
        for i, clip in enumerate(clips):
            if clip:
                try:
                    clip.close()
                except Exception as e:
                    print(f"Warning: Error closing clip {i}: {e}")

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
    final_video = None
    reference_size = None
    
    try:
        # Load video clips and check compatibility
        for i, path in enumerate(video_paths):
            print(f"Loading video {i+1}/{len(video_paths)}: {os.path.basename(path)}")
            
            # Get video info using OpenCV for quick size check
            if check_compatibility:
                cap = None
                try:
                    cap = cv2.VideoCapture(path)
                    if not cap.isOpened():
                        raise ValueError(f"Cannot open video file: {path}")
                    
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    current_size = (width, height)
                    
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
                        
                finally:
                    if cap:
                        cap.release()
            
            # Load with MoviePy
            clip = VideoFileClip(path)
            video_clips.append(clip)
            print(f"Loaded: {os.path.basename(path)} - Duration: {clip.duration:.2f}s")
        
        # Concatenate videos
        print("Concatenating videos...")
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write output
        print(f"Writing concatenated video to: {output_file}")
        final_video.write_videofile(
            output_file,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",        # 🚀 FASTEST preset (was "medium")
            bitrate="3000k",          # 🚀 LOWER bitrate (was "8000k") 
            audio_bitrate="64k",      # 🚀 LOWER audio quality (was "128k")
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
             ffmpeg_params=[
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-crf", "28",             # 🚀 HIGHER compression = faster
                "-tune", "fastdecode"     # 🚀 OPTIMIZE for speed
            ],
            threads=4,
            logger=None               # 🚀 DISABLE verbose logging
        )
        
        total_duration = sum(clip.duration for clip in video_clips)
        print(f"Successfully concatenated {len(video_paths)} videos")
        print(f"Total duration: {total_duration:.2f}s")
        print(f"Output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error during concatenation: {str(e)}")
        traceback.print_exc()
        return False
        
    finally:
        # Clean up resources
        print("Cleaning up concatenation resources...")
        
        if final_video:
            try:
                final_video.close()
            except Exception as e:
                print(f"Warning: Error closing final_video: {e}")
        
        # Clean up clips
        for i, clip in enumerate(video_clips):
            if clip:
                try:
                    clip.close()
                except Exception as e:
                    print(f"Warning: Error closing clip {i}: {e}")

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
    final_audio = None
    silence_clip = None
    
    try:
        # Load all audio clips
        for i, path in enumerate(audio_paths):
            if not os.path.exists(path):
                print(f"Warning: Audio file not found: {path}")
                continue
                
            print(f"Loading audio {i+1}/{len(audio_paths)}: {os.path.basename(path)}")
            
            try:
                clip = AudioFileClip(path)
                audio_clips.append(clip)
                print(f"Loaded: {os.path.basename(path)} - Duration: {clip.duration:.2f}s")
            except Exception as e:
                print(f"Error loading audio file {path}: {e}")
                continue
                
        if not audio_clips:
            print("No valid audio clips found")
            return False
        
        # Insert silence between clips if requested
        clips_to_concatenate = audio_clips
        if silence_between > 0 and len(audio_clips) > 1:
            try:
                from moviepy.audio.AudioClip import AudioClip
                silence_clip = AudioClip(lambda t: 0, duration=silence_between)
                clips_with_silence = []
                
                for i, clip in enumerate(audio_clips):
                    clips_with_silence.append(clip)
                    if i < len(audio_clips) - 1:  # Don't add silence after last clip
                        clips_with_silence.append(silence_clip)
                        
                clips_to_concatenate = clips_with_silence
                print(f"Inserted {silence_between}s silence between clips")
            except Exception as e:
                print(f"Error creating silence clips: {e}")
                clips_to_concatenate = audio_clips  # Fall back to no silence
        
        # Concatenate audio clips
        print("Concatenating audio clips...")
        final_audio = concatenate_audioclips(clips_to_concatenate)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write the final audio to file
        print(f"Writing concatenated audio to: {output_file}")
        final_audio.write_audiofile(output_file)
        
        total_duration = final_audio.duration
        print(f"Successfully concatenated {len(audio_clips)} audio clips")
        print(f"Total duration: {total_duration:.2f}s")
        print(f"Output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"Error during audio concatenation: {str(e)}")
        traceback.print_exc()
        return False
        
    finally:
        # Clean up resources
        print("Cleaning up audio concatenation resources...")
        
        if final_audio:
            try:
                final_audio.close()
            except Exception as e:
                print(f"Warning: Error closing final_audio: {e}")
        
        if silence_clip:
            try:
                silence_clip.close()
            except Exception as e:
                print(f"Warning: Error closing silence_clip: {e}")
        
        # Clean up individual audio clips
        for i, clip in enumerate(audio_clips):
            if clip:
                try:
                    clip.close()
                except Exception as e:
                    print(f"Warning: Error closing audio clip {i}: {e}")

def resolve_path(path: str, base_path: str) -> str:
    """
    Resolves a path relative to the specified base_path to an absolute path.
    If the path is already absolute, returns it unchanged.
    
    Args:
        path: A relative or absolute file path
        base_path: The base directory to resolve relative paths against (defaults to BASE_DIRECTORY_TT)
        
    Returns:
        str: An absolute file path
    """
    if not path:
        return ""
        
    # If path is already absolute, return it
    if os.path.isabs(path):
        return path
        
    # Otherwise join with base_path
    return os.path.join(base_path, path)

def add_voice_to_video(video_path: str, voice_path: str, output_path: str = None, output_dir: str = None) -> str:
    """
    Add voice audio to an existing video with music, placing the voice in the middle of the video timeline.
    Optimized for FFmpeg concatenation with create_video_with_audio function.
    
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
    video_clip = None
    voice_audio = None
    original_audio = None
    composite_audio = None
    final_video = None
    
    try:
        # Load the video
        video_clip = VideoFileClip(video_path)
        
        # Load the voice audio
        voice_audio = AudioFileClip(voice_path)
        
        # Check if voice is longer than video
        if voice_audio.duration > video_clip.duration:
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
        
        # 🚀 OPTIMIZED: Use IDENTICAL settings to create_video_with_audio for perfect FFmpeg concat compatibility
        final_video.write_videofile(
            result_path,
            fps=12,                    # MATCH: Same as main clip
            codec="libx264",           # MATCH: Same codec
            audio_codec="aac",         # MATCH: Same audio codec
            preset="slow",             # MATCH: Same preset for quality
            bitrate="1500k",           # MATCH: Same bitrate
            audio_bitrate="128k",      # MATCH: Same audio bitrate
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            ffmpeg_params=[
                "-pix_fmt", "yuv420p",         # MATCH: Same pixel format
                "-movflags", "+faststart",     # MATCH: Same movflags
                "-crf", "23",                  # MATCH: Same quality
                "-tune", "stillimage",         # MATCH: Same tuning (if head/tail are static-like)
                "-g", "120",                   # MATCH: Same GOP size
                "-keyint_min", "12",           # MATCH: Same minimum keyframes
                "-profile:v", "high",          # MATCH: Same profile
                "-level", "4.0",               # MATCH: Same level
                "-maxrate", "2250k",           # MATCH: Same max bitrate
                "-bufsize", "4500k",           # MATCH: Same buffer size
                "-colorspace", "bt709",        # MATCH: Same colorspace
                "-color_primaries", "bt709",   # MATCH: Same color primaries
                "-color_trc", "bt709"          # MATCH: Same color transfer
            ],
            threads=4,                 # MATCH: Same thread count
            logger=None                # MATCH: Silent logging
        )
        
        print(f"✅ Successfully added voice to video with FFmpeg-optimized encoding: {result_path}")
        return result_path
        
    except Exception as e:
        print(f"❌ Error adding voice to video: {str(e)}")
        traceback.print_exc()
        return None
        
    finally:
        # Clean up resources
        print("Cleaning up add_voice_to_video resources...")
        
        cleanup_items = [
            ("final_video", final_video),
            ("composite_audio", composite_audio),
            ("original_audio", original_audio),
            ("voice_audio", voice_audio),
            ("video_clip", video_clip)
        ]
        
        for name, item in cleanup_items:
            if item is not None:
                try:
                    print(f"Closing {name}")
                    item.close()
                except Exception as cleanup_error:
                    print(f"Warning: Error closing {name}: {cleanup_error}")


def concatenate_videos_ffmpeg(video_paths: List[str], output_path: str) -> bool:
    """
    Concatenate videos using FFmpeg's concat demuxer - much faster than MoviePy
    
    Args:
        video_paths: List of video file paths to concatenate
        output_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create temporary file list for FFmpeg
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            filelist_path = f.name
            for video_path in video_paths:
                # Escape single quotes and write to file list
                escaped_path = video_path.replace("'", "'\"'\"'")
                f.write(f"file '{escaped_path}'\n")
        
        # Run FFmpeg concat
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', filelist_path,
            '-c', 'copy',  # Stream copy - no re-encoding!
            '-y',  # Overwrite output
            output_path
        ]
        
        print(f"🔄 FFmpeg concatenating {len(video_paths)} videos...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"✅ FFmpeg concatenation successful: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg concatenation failed: {e}")
        print(f"FFmpeg stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error during concatenation: {e}")
        return False
    finally:
        # Clean up temporary file
        try:
            os.unlink(filelist_path)
        except:
            pass

def concatenate_videos_ffmpeg_with_reencoding(video_paths: List[str], output_path: str) -> bool:
    """
    Concatenate videos with re-encoding - use when videos have different formats
    """
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            filelist_path = f.name
            for video_path in video_paths:
                escaped_path = video_path.replace("'", "'\"'\"'")
                f.write(f"file '{escaped_path}'\n")
        
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', filelist_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '22',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-y',
            output_path
        ]
        
        print(f"🔄 FFmpeg concatenating with re-encoding...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"✅ FFmpeg concatenation with re-encoding successful")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg concatenation failed: {e}")
        return False
    finally:
        try:
            os.unlink(filelist_path)
        except:
            pass