from video_common import add_text_to_image, TextStyle
import os

def test_image_text_overlay():
    # Test parameters
    image_path = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot\TT\Дама в розовом.png"
    
    textForTitle = "Дама в\nрозовом"
    horizontal_offsetForTitle = 30  # centered
    vertical_offsetForTitle = 35    # near bottom with extra space
    
    # Custom style (optional)
    styleForTitle = TextStyle(
        font_size=90,
        text_color="black",
        stroke_color="black",
        stroke_width=0
    )

    textForAuthor = "Гребенщиков \nГеоргий Дмитриевич".upper()
    horizontal_offsetForAuthor = 30  # centered
    vertical_offsetForAuthor = 3    # near bottom with extra space
    
    # Custom style (optional)
    styleForAuthor = TextStyle(
        font_size=30,
        text_color="black",
        stroke_color="black",
        stroke_width=0
    )

    
    # Process image
    result_path = add_text_to_image(
        image_path=image_path,
        text=textForTitle,
        horizontal_offset=horizontal_offsetForTitle,
        vertical_offset=vertical_offsetForTitle,
        style=styleForTitle
    )

       # Process image
    result_path = add_text_to_image(
        image_path=result_path,
        text=textForAuthor,
        horizontal_offset=horizontal_offsetForAuthor,
        vertical_offset=vertical_offsetForAuthor,
        style=styleForAuthor
    )

    
    if result_path:
        print(f"Successfully created image: {result_path}")
    else:
        print("Failed to process image")

if __name__ == "__main__":
    test_image_text_overlay()