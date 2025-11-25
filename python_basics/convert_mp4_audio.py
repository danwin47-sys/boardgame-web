from moviepy.editor import VideoFileClip

input_path = r"C:\Users\judy\Desktop\test\video1.mp4"
output_path = r"C:\Users\judy\Desktop\test\video1.mp3"

video = VideoFileClip(input_path)
video.audio.write_audiofile(output_path)