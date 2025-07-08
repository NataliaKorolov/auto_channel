from video_common import get_texts_from_csv, add_text_overlay, resize_and_crop_clip
import os
import pandas as pd
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from moviepy.video.VideoClip import ImageClip, TextClip, CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "TimelessTales.csv")

def create_video(image_path, title, author, audio_path, result_path):
    audio = AudioFileClip(audio_path)
    img_clip = ImageClip(image_path).set_duration(audio.duration)
    w, h = img_clip.size

    left_2_3_w = int(w * 2 / 3)

    # Title in the middle of left 2/3
    title_clip = TextClip(
        title,
        fontsize=60,
        color='white',
        font="Arial",
        size=(left_2_3_w, None),
        method="caption"
    ).set_duration(audio.duration).set_position(
        (int(w * 0.0), int(h * 0.4))
    )

    # Author at the bottom of left 2/3
    author_clip = TextClip(
        author,
        fontsize=40,
        color='white',
        font="Arial",
        size=(left_2_3_w, None),
        method="caption"
    ).set_duration(audio.duration).set_position(
        (int(w * 0.0), int(h * 0.85))
    )

    video = CompositeVideoClip([img_clip, title_clip, author_clip])
    video = video.set_audio(audio)
    video.write_videofile(result_path, fps=24, codec='libx264', audio_codec='aac')

    return audio.duration

def main():
    df = get_texts_from_csv(CSV_PATH)
    results = []

    for idx, row in df.iterrows():
        image_path = os.path.join(BASE_DIR, str(row['Image']))
        audio_path = os.path.join(BASE_DIR, str(row['Audio']))
        author = str(row['Author']).strip()
        title = str(row['Title']).strip()
        result_filename = f"{author} {title}.mp4".replace("/", "_").replace("\\", "_")
        result_path = os.path.join(BASE_DIR, result_filename)

        audio_length = create_video(image_path, title, author, audio_path, result_path)
        results.append(audio_length)

    df['Result_Automation'] = results
    df.to_csv(CSV_PATH, index=False)

if __name__ == "__main__":
    main()