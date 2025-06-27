import os
from moviepy import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

BASE = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot"
video_paths = [os.path.join(BASE, f"prompt {i}.mp4") for i in range(1, 11)]
audio_path = os.path.join(BASE, "ElevenLabs_300 Final.mp3")

def make_and_export(output_file, size, resize_dim):
    clips = []
    for p in video_paths:
        clip = VideoFileClip(p)
        if resize_dim == "height":
            clip = clip.resized(height=size[1]).cropped(x_center=clip.w/2, width=size[0])
        else:
            clip = clip.resized(width=size[0]).cropped(y_center=clip.h/2, height=size[1])
        clips.append(clip)

    final_clip = concatenate_videoclips(clips, method="compose")
    audio_clip = AudioFileClip(audio_path).subclipped(0, final_clip.duration)
    final_with_audio = final_clip.with_audio(audio_clip)
    final_with_audio.write_videofile(
    output_file,
    codec="libx264",
    audio_codec="aac",
    preset="ultrafast",
    bitrate="20000k",
    audio_fps=44100,
    logger=None
)

if __name__ == "__main__":
    make_and_export(os.path.join(BASE, "final_horizontal_1920x1080.mp4"),
                    (1920, 1080), "height")
    make_and_export(os.path.join(BASE, "final_vertical_1080x1920.mp4"),
                    (1080, 1920), "width")
