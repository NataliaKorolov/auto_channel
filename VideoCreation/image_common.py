"""
Image processing utilities for creating static images with text overlays.
This module provides PIL-based image processing functions, which are much more
efficient than MoviePy for static image manipulation.
"""

import os
import textwrap
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass

# Import shared data structures from video_common
try:
    from video_common import TextOverlay, TextStyle, BASE_DIRECTORY
except ImportError:
    # Fallback definitions if video_common is not available
    @dataclass
    class TextStyle:
        font_size: int = 60
        text_color: str = "white"
        stroke_color: str = "black"
        stroke_width: int = 2

    @dataclass
    class TextOverlay:
        text: str
        horizontal_offset: int  # 1-100, percentage within the left panel
        vertical_offset: int    # 1-100, percentage within the left panel (100 = top)
        style: TextStyle

    BASE_DIRECTORY = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot"


def create_image_with_text_overlays_static(
    image_path: str,
    text_overlays: List[TextOverlay],
    output_dir: str = os.path.join(BASE_DIRECTORY, "TT", "assets", "portraits with overlays"),
    *,
    # safe area (top, right, bottom, left) in %
    safe_area_pct: Tuple[int, int, int, int] = (5, 6, 14, 6),
    # where the left panel ends, as % of width (e.g., your portrait starts at ~62%)
    panel_split_pct: float = 62.0,
    # cap text wrapping width within the target region
    max_text_width_ratio: float = 0.90,
    # Font settings
    font_path: str = None,  # Path to TTF font file, None for default
    max_font_size: int = 100,  # Maximum font size to try
    min_font_size: int = 20,   # Minimum font size
    line_spacing_ratio: float = 1.2,  # Line spacing multiplier
    center_text_horizontally: bool = True  # NEW: Always center text horizontally in left panel
) -> str:
    """
    Create a static image with text overlays using PIL.
    Much more efficient than MoviePy for static image processing.
    
    Args:
        image_path: Path to the source image
        text_overlays: List of TextOverlay objects
        output_dir: Directory to save the result image
        safe_area_pct: Safe area margins (top, right, bottom, left) in %
        panel_split_pct: Where the left panel ends as % of width
        max_text_width_ratio: Maximum text width ratio within the target region
        font_path: Path to TTF font file (optional)
        max_font_size: Maximum font size to try
        min_font_size: Minimum font size
        line_spacing_ratio: Line spacing multiplier
        center_text_horizontally: If True, always center text horizontally in left panel
        
    Returns:
        str: Path to the created image file, or empty string on error
    """
    try:
        # Validate input
        if not os.path.exists(image_path):
            raise ValueError(f"Image path does not exist: {image_path}")

        if not text_overlays:
            raise ValueError("No text overlays provided")

        for i, overlay in enumerate(text_overlays):
            if not (1 <= overlay.horizontal_offset <= 100 and 1 <= overlay.vertical_offset <= 100):
                raise ValueError(f"Overlay {i}: Offset values must be between 1 and 100")

        # Load the image
        img = Image.open(image_path).convert('RGBA')
        W, H = img.size
        print(f"📐 Image size: {W}x{H}")

        # Create a transparent overlay for text
        txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Calculate safe area and left panel region
        top_p, right_p, bottom_p, left_p = safe_area_pct
        safe_left = int(W * (left_p / 100.0))
        safe_right = W - int(W * (right_p / 100.0))
        safe_top = int(H * (top_p / 100.0))
        safe_bottom = H - int(H * (bottom_p / 100.0))

        # Left panel region (safe area ∩ left segment)
        split_x = int(W * (panel_split_pct / 100.0))
        region_left = safe_left
        region_right = min(safe_right, split_x)
        region_top = safe_top
        region_bottom = safe_bottom
        region_w = max(1, region_right - region_left)
        region_h = max(1, region_bottom - region_top)

        print(f"🛟 Text region: {region_left},{region_top} to {region_right},{region_bottom} → {region_w}x{region_h}")
        print(f"📐 Panel split at {panel_split_pct}% = {split_x}px")

        # Process each text overlay
        for i, overlay in enumerate(text_overlays):
            try:
                print(f"📝 Processing text {i+1}: '{overlay.text[:50]}...'")
                
                # Calculate maximum text width
                max_text_w = int(region_w * max_text_width_ratio)
                
                # Auto-wrap text and find optimal font size
                wrapped_text, final_font, text_w, text_h = fit_text_to_region(
                    text=overlay.text,
                    max_width=max_text_w,
                    max_height=region_h - 20,  # Leave some margin
                    font_path=font_path,
                    max_font_size=min(overlay.style.font_size, max_font_size),
                    min_font_size=min_font_size,
                    line_spacing_ratio=line_spacing_ratio
                )

                if not wrapped_text:
                    print(f"⚠️ Could not fit text {i+1} in region")
                    continue

                # 🎯 IMPROVED: Calculate position within the region
                if center_text_horizontally:
                    # Always center horizontally in the left panel
                    cx = region_w // 2
                    print(f"🎯 Centering text horizontally at x={cx} (region center)")
                else:
                    # Use horizontal_offset as before
                    cx = region_left + int((overlay.horizontal_offset / 100.0) * region_w)
                    print(f"🎯 Positioning text at {overlay.horizontal_offset}% horizontally = x={cx}")
                
                # Vertical position uses the vertical_offset
                cy = region_top + int(((100 - overlay.vertical_offset) / 100.0) * region_h)
                print(f"🎯 Positioning text at {overlay.vertical_offset}% vertically = y={cy}")

                # Calculate final text position (top-left corner)
                x_pos = cx - text_w // 2
                y_pos = cy - text_h // 2

                # Ensure text stays within region bounds
                x_pos = max(region_left, min(x_pos, region_right - text_w))
                y_pos = max(region_top, min(y_pos, region_bottom - text_h))

                print(f"📍 Text {i+1} final position: ({x_pos},{y_pos}), size: {text_w}x{text_h}")

                # Convert colors to RGBA tuples if they're strings
                text_color = parse_color(overlay.style.text_color)
                stroke_color = parse_color(overlay.style.stroke_color)

                # Draw the text with stroke if specified
                if overlay.style.stroke_width > 0:
                    # Draw stroke by drawing text in multiple positions
                    for adj_x in range(-overlay.style.stroke_width, overlay.style.stroke_width + 1):
                        for adj_y in range(-overlay.style.stroke_width, overlay.style.stroke_width + 1):
                            if adj_x != 0 or adj_y != 0:
                                draw.multiline_text(
                                    (x_pos + adj_x, y_pos + adj_y),
                                    wrapped_text,
                                    font=final_font,
                                    fill=stroke_color,
                                    align = "center",
                                    spacing=int(final_font.size * (line_spacing_ratio - 1))
                                )

                # Draw the main text
                draw.multiline_text(
                    (x_pos, y_pos),
                    wrapped_text,
                    font=final_font,
                    fill=text_color,
                    align = "center",
                    spacing=int(final_font.size * (line_spacing_ratio - 1))
                )

                print(f"✅ Added text overlay {i+1}")

            except Exception as e:
                print(f"❌ Error processing text overlay {i+1}: {e}")
                continue

        # Combine the original image with the text layer
        final_img = Image.alpha_composite(img, txt_layer)
        final_img = final_img.convert('RGB')  # Convert back to RGB for saving

        # Generate output filename
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename based on first text overlay
        first_text = text_overlays[0].text if text_overlays else "overlay"
        safe_text = "".join(c for c in first_text if c.isalnum() or c in (' ', '-', '_')).rstrip()[:30]
        safe_text = safe_text.replace(' ', '_')
        
        input_name = os.path.splitext(os.path.basename(image_path))[0]
        output_filename = f"{input_name}_{safe_text}_overlay.png"
        output_path = os.path.join(output_dir, output_filename)

        # Save the image
        final_img.save(output_path, 'PNG', quality=95)
        print(f"💾 Saved image with overlays: {output_path}")

        return output_path

    except Exception as e:
        print(f"❌ Error creating image with overlays: {e}")
        import traceback
        traceback.print_exc()
        return ""


def fit_text_to_region(
    text: str,
    max_width: int,
    max_height: int,
    font_path: str = None,
    max_font_size: int = 100,
    min_font_size: int = 20,
    line_spacing_ratio: float = 1.2
) -> Tuple[str, ImageFont.ImageFont, int, int]:
    """
    Fit text to a region by adjusting font size and wrapping text.
    
    Returns:
        Tuple of (wrapped_text, font, text_width, text_height)
    """
    for font_size in range(max_font_size, min_font_size - 1, -2):
        try:
            # Load font
            font = load_font(font_path, font_size)

            # Calculate characters per line based on average character width
            sample_text = "ABCDEabcde"
            bbox = font.getbbox(sample_text)
            avg_char_width = (bbox[2] - bbox[0]) / len(sample_text)
            chars_per_line = max(10, int(max_width / avg_char_width))
            
            # Wrap text
            wrapped_lines = textwrap.wrap(text, width=chars_per_line)
            if not wrapped_lines:  # Handle empty text
                wrapped_lines = [text]
            wrapped_text = '\n'.join(wrapped_lines)
            
            # Calculate text dimensions
            text_width, text_height = calculate_text_dimensions(
                wrapped_text, font, line_spacing_ratio
            )
            
            # Check if text fits
            if text_width <= max_width and text_height <= max_height:
                print(f"✅ Text fits with font size {font_size}: {text_width}x{text_height}")
                return wrapped_text, font, text_width, text_height
                
        except Exception as e:
            print(f"⚠️ Error trying font size {font_size}: {e}")
            continue
    
    # If no size worked, return the smallest size attempt
    print(f"⚠️ Text doesn't fit well, using minimum font size {min_font_size}")
    font = load_font(font_path, min_font_size)
    
    # Use more aggressive wrapping for minimum size
    sample_text = "ABCDEabcde"
    bbox = font.getbbox(sample_text)
    avg_char_width = (bbox[2] - bbox[0]) / len(sample_text)
    chars_per_line = max(5, int(max_width / avg_char_width))
    
    wrapped_lines = textwrap.wrap(text, width=chars_per_line)
    if not wrapped_lines:
        wrapped_lines = [text]
    wrapped_text = '\n'.join(wrapped_lines)
    
    text_width, text_height = calculate_text_dimensions(
        wrapped_text, font, line_spacing_ratio
    )
    
    return wrapped_text, font, text_width, text_height


def load_font(font_path: str = None, font_size: int = 20) -> ImageFont.ImageFont:
    """
    Load a font with fallback options.
    
    Args:
        font_path: Path to TTF font file (optional)
        font_size: Font size
        
    Returns:
        ImageFont object
    """
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"⚠️ Could not load font {font_path}: {e}")
    
    # Try common system fonts
    font_candidates = [
        "arial.ttf",
        "Arial.ttf",
        "DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf",
        "calibri.ttf",
        "times.ttf"
    ]
    
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, font_size)
        except:
            continue
    
    # Fallback to default font
    try:
        return ImageFont.load_default()
    except:
        # Last resort - create a basic font
        return ImageFont.load_default()


def calculate_text_dimensions(
    text: str, 
    font: ImageFont.ImageFont, 
    line_spacing_ratio: float = 1.2
) -> Tuple[int, int]:
    """
    Calculate the dimensions of multiline text.
    
    Args:
        text: The text (can be multiline)
        font: PIL ImageFont object
        line_spacing_ratio: Line spacing multiplier
        
    Returns:
        Tuple of (width, height)
    """
    lines = text.split('\n')
    if not lines:
        return 0, 0
    
    max_width = 0
    total_height = 0
    
    for i, line in enumerate(lines):
        if line.strip():  # Non-empty line
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
        else:  # Empty line
            bbox = font.getbbox("A")  # Use 'A' as reference
            line_width = 0
            line_height = bbox[3] - bbox[1]
        
        max_width = max(max_width, line_width)
        total_height += line_height
        
        # Add line spacing (except for the last line)
        if i < len(lines) - 1:
            total_height += int(line_height * (line_spacing_ratio - 1))
    
    return max_width, total_height


def parse_color(color) -> Tuple[int, int, int, int]:
    """
    Parse a color string or tuple into RGBA tuple.
    
    Args:
        color: Color as string (hex, name) or tuple (RGB, RGBA)
        
    Returns:
        RGBA tuple (r, g, b, a)
    """
    if isinstance(color, str):
        if color.startswith('#'):
            # Hex color
            color = color[1:]
            if len(color) == 3:
                # Short hex (e.g., #RGB -> #RRGGBB)
                color = ''.join([c*2 for c in color])
            if len(color) == 6:
                r = int(color[0:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:6], 16)
                return (r, g, b, 255)
            elif len(color) == 8:
                r = int(color[0:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:6], 16)
                a = int(color[6:8], 16)
                return (r, g, b, a)
        else:
            # Named color - try to convert using PIL
            try:
                from PIL import ImageColor
                rgba = ImageColor.getrgb(color)
                if len(rgba) == 3:
                    return rgba + (255,)
                return rgba
            except:
                # Fallback to white if color name not recognized
                return (255, 255, 255, 255)
    
    elif isinstance(color, (tuple, list)):
        if len(color) == 3:
            return tuple(color) + (255,)
        elif len(color) == 4:
            return tuple(color)
    
    # Default fallback
    return (255, 255, 255, 255)


def test_image_overlays():
    """
    Test function to create sample images with text overlays.
    This is your trial run function!
    """
    print("🧪 Starting image overlay test...")
    
    # Test image path (adjust this to your actual test image)
    test_image_path = os.path.join(BASE_DIRECTORY, "TT", "assets", "test_portrait.jpg")
    
    # Check if test image exists
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        print("📁 Please place a test image there first!")
        return None
    
    # Create some test overlays
    test_overlays = [
        TextOverlay(
            text="The brave knight stood tall against the stormy sky, his armor gleaming in the lightning.",
            horizontal_offset=50,  # Center horizontally
            vertical_offset=30,    # Upper portion
            style=TextStyle(
                font_size=60,
                text_color="#FFD700",  # Gold
                stroke_color="black",
                stroke_width=2
            )
        ),
        TextOverlay(
            text="Chapter 1: The Beginning",
            horizontal_offset=50,
            vertical_offset=70,    # Lower portion
            style=TextStyle(
                font_size=40,
                text_color="white",
                stroke_color="navy",
                stroke_width=3
            )
        )
    ]
    
    # Create the image with overlays
    result_path = create_image_with_text_overlays_static(
        image_path=test_image_path,
        text_overlays=test_overlays
    )
    
    if result_path:
        print(f"✅ Test completed! Result saved to: {result_path}")
        return result_path
    else:
        print("❌ Test failed!")
        return None


def create_test_overlays():
    """Create multiple test images with different text overlay scenarios"""
    
    # You'll need to put a test image here
    test_image_path = os.path.join(BASE_DIRECTORY, "TT", "assets", "portraits", "test_image.jpg")
    
    # Check if test image exists
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        print("📁 Please place a test image there first!")
        return []
    
    # Create different test scenarios
    test_scenarios = [
        {
            "name": "Golden_Title",
            "overlays": [
                TextOverlay(
                    text="The Ancient Tale of Heroes and Legends",
                    horizontal_offset=50,
                    vertical_offset=25,
                    style=TextStyle(
                        font_size=70,
                        text_color="#FFD700",  # Gold
                        stroke_color="black",
                        stroke_width=3
                    )
                )
            ]
        },
        {
            "name": "Multi_Text",
            "overlays": [
                TextOverlay(
                    text="Chapter 1",
                    horizontal_offset=50,
                    vertical_offset=20,
                    style=TextStyle(
                        font_size=50,
                        text_color="white",
                        stroke_color="navy",
                        stroke_width=2
                    )
                ),
                TextOverlay(
                    text="In a land far away, where magic still flows through the ancient stones...",
                    horizontal_offset=50,
                    vertical_offset=60,
                    style=TextStyle(
                        font_size=40,
                        text_color="#FFE4B5",  # Light golden
                        stroke_color="darkred",
                        stroke_width=2
                    )
                )
            ]
        },
        {
            "name": "Simple_Quote",
            "overlays": [
                TextOverlay(
                    text='"Courage is not the absence of fear, but action in spite of it."',
                    horizontal_offset=50,
                    vertical_offset=50,
                    style=TextStyle(
                        font_size=45,
                        text_color="#F0F8FF",  # Alice blue
                        stroke_color="#2F4F4F",  # Dark slate gray
                        stroke_width=2
                    )
                )
            ]
        }
    ]
    
    results = []
    for scenario in test_scenarios:
        print(f"\n🎨 Creating {scenario['name']} overlay...")
        
        result_path = create_image_with_text_overlays_static(
            image_path=test_image_path,
            text_overlays=scenario['overlays']
        )
        
        if result_path:
            results.append(result_path)
            print(f"✅ Created: {result_path}")
        else:
            print(f"❌ Failed to create {scenario['name']}")
    
    print(f"\n🎉 Test completed! Created {len(results)} images:")
    for path in results:
        print(f"   📁 {path}")
    
    return results


if __name__ == "__main__":
    # Run tests when script is executed directly
    create_test_overlays()
