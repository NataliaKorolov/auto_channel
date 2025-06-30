import os
from moviepy import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

BASE = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot"
video_paths = [os.path.join(BASE, f"prompt {i}.mp4") for i in range(1, 11)]
audio_path = os.path.join(BASE, "ElevenLabs_300 Final.mp3")

MIN_DURATION = 60  # seconds

def make_and_export(output_file, size, resize_dim):
    clips = []
    for p in video_paths:
        if not os.path.exists(p):
            print(f"Warning: {p} not found. Skipping.")
            continue
        clip = VideoFileClip(p)
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
        clips.append(clip)

    if not clips:
        print("No video clips found. Exiting.")
        return

    # Concatenate and loop if needed to reach at least MIN_DURATION
    final_clip = concatenate_videoclips(clips, method="compose")
    if final_clip.duration < MIN_DURATION:
        loops = int(MIN_DURATION // final_clip.duration) + 1
        looped = [final_clip] * loops
        final_clip = concatenate_videoclips(looped, method="compose")
    # Trim to exactly MIN_DURATION
    final_clip = final_clip.subclipped(0, MIN_DURATION)

    # Prepare audio
    audio_clip = AudioFileClip(audio_path).subclipped(0, MIN_DURATION)
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

def make_and_export_blur(output_file, size):
    try:
        import cv2
    except ImportError:
        print("OpenCV (cv2) is not installed. Please run 'pip install opencv-python' to enable blurred background.")
        return
    clips = []
    for p in video_paths:
        if not os.path.exists(p):
            print(f"Warning: {p} not found. Skipping.")
            continue
        clip = VideoFileClip(p)
        fg_clip = clip.resized(width=size[0])
        # Try to use fl_image for OpenCV blur, else fallback to black background
        blur_supported = hasattr(clip, 'fl_image')
        if blur_supported:
            def blur_frame(frame):
                return cv2.GaussianBlur(frame, (99, 99), 50)
            bg_clip = clip.resized(height=size[1]).fl_image(blur_frame)
            bg_clip = bg_clip.set_position((0, 0)).set_opacity(1)
        else:
            print("fl_image not available in this MoviePy version. Using solid black background.")
            from moviepy.video.VideoClip import ColorClip
            bg_clip = ColorClip(size=size, color=(0, 0, 0)).with_duration(clip.duration)
        fg_y = (size[1] - fg_clip.h) // 2
        fg_clip = fg_clip.set_position((0, fg_y))
        comp = CompositeVideoClip([bg_clip, fg_clip], size=size).set_duration(clip.duration)
        clips.append(comp)

    if not clips:
        print("No video clips found. Exiting.")
        return

    final_clip = concatenate_videoclips(clips, method="compose")
    if final_clip.duration < MIN_DURATION:
        loops = int(MIN_DURATION // final_clip.duration) + 1
        looped = [final_clip] * loops
        final_clip = concatenate_videoclips(looped, method="compose")
    final_clip = final_clip.subclipped(0, MIN_DURATION)

    audio_clip = AudioFileClip(audio_path).subclipped(0, MIN_DURATION)
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

if __name__ == "__main__":
    # For vertical 1080x1920 output (TikTok/Instagram), always use resize_dim="height"
    make_and_export(os.path.join(BASE, "final_vertical_1080x1920.mp4"),
                    (1080, 1920), "height")
    # For horizontal 1920x1080 output (YouTube), use resize_dim="width" if needed
    make_and_export(os.path.join(BASE, "final_horizontal_1920x1080.mp4"),
                    (1920, 1080), "width")
