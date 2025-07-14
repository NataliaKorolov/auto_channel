import pandas as pd
from typing import List, Tuple
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import TextClip, ImageClip  # Added ImageClip import
from dataclasses import dataclass
from pathlib import Path
from PIL import Image
import re
from pathlib import Path
import os

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
    output_dir: str = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot"
) -> str:
    """
    Add text to an image with specified positioning and style.
    
    Args:
        image_path: Path to the input image
        text: Text to overlay on the image
        horizontal_offset: Percentage from left (1-100)
        vertical_offset: Percentage from bottom (1-100)
        style: TextStyle configuration
        output_dir: Directory for output file
        
    Returns:
        Path to the processed image
    """
    try:
        # Validate inputs
        if not os.path.exists(image_path):
            raise ValueError(f"Image path does not exist: {image_path}")
        if not (1 <= horizontal_offset <= 100 and 1 <= vertical_offset <= 100):
            raise ValueError("Offset values must be between 1 and 100")

        # Create output filename

        text_cleaned = re.sub(r'[\\/*?:"<>|\n]', '_', text).replace(' ', '_')
        output_filename = f"{Path(image_path).stem}_{text_cleaned}{Path(image_path).suffix}"
        output_path = os.path.join(output_dir, output_filename)

        # Load image
        img = Image.open(image_path)
        
        # Create text clip with padding
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
        x_pos = int((img.width * horizontal_offset) / 100) - txt_clip.w // 2  # Center horizontally
        y_pos = int(img.height * (100 - vertical_offset) / 100) - txt_clip.h - 20  # Add 20px bottom margin
        
        # Create composite
        result = CompositeVideoClip([
            ImageClip(image_path),
            txt_clip.with_position((x_pos, y_pos))
        ])
        
        # Save result
        result.save_frame(output_path)
        
        return output_path

    except Exception as e:
        print(f"Error processing image: {e}")
        return ""