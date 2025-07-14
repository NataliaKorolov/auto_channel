from video_common import add_text_to_image, TextStyle, create_video_with_audio
import os

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

if __name__ == "__main__":
    result_clip = test_image_text_overlay()
    if result_clip:
        video_path = create_video_with_audio(result_clip, audio_path)
        if video_path:
            print(f"Successfully created video: {video_path}")
        else:
            print("Failed to create video")