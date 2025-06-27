import os
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip

# Define paths
media_folder = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot"
output_file = os.path.join(media_folder, "final_video.mp4")

# List of video filenames
video_filenames = [f"Prompt {i}_resized YT.mp4" for i in range(1, 11)]
video_paths = [os.path.join(media_folder, fname) for fname in video_filenames]

# Load video clips
print("Loading video clips...")
video_clips = [VideoFileClip(path) for path in video_paths]

# Concatenate all video clips
print("Combining video clips...")
final_video = concatenate_videoclips(video_clips, method="compose")

# Load audio file
print("Adding audio track...")
audio_path = os.path.join(media_folder, "ElevenLabs_Greece Ahill_RU.mp3")
audio = AudioFileClip(audio_path)

# Set audio to the final video
final_video = final_video.with_audio(audio)

# Export the final video
print(f"Exporting final video to: {output_file}")
final_video.write_videofile(output_file, codec="libx264", audio_codec="aac")

print("Done!")
