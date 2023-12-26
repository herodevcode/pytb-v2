import os
import pytube
import streamlit as st
from moviepy.editor import VideoFileClip
from datetime import time, timedelta

## pip install -r requirements.txt
## streamlit run main.py

def download_video(url, output_path, start_time=None, end_time=None, video_title=None):
    yt = pytube.YouTube(url)
    video = yt.streams.get_highest_resolution()
    
    if video_title is None:
        video_title = yt.title
    final_output_filename = f"{video_title}.mp4"
    final_output_file = os.path.join(output_path, final_output_filename)

    if start_time is not None and end_time is not None:
        temp_output_file = os.path.join(output_path, video.default_filename)
        video.download(output_path=output_path) 

        # Convert time objects to seconds
        start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second

        # Cut the video
        with VideoFileClip(temp_output_file) as video_clip:
            video_segment = video_clip.subclip(start_seconds, end_seconds)
            video_segment.write_videofile(final_output_file, codec="libx264", audio_codec="aac")

        os.remove(temp_output_file)  # Remove the original, full-length video
    else:
        video.download(filename=final_output_filename, output_path=output_path) 

    return final_output_file

if __name__ == '__main__':
    st.title("YouTube Video Downloader")

    url = st.text_input('YouTube URL')
    use_timestamps = st.checkbox('Specify Timestamps')

    start_time = end_time = None
    video_title = None

    if use_timestamps:
        default_start_time = time(0, 0)  # Default time interpreted as 0 hours, minutes, and seconds
        default_end_time = time(0, 0)
        start_time = st.time_input("Start Time (HH:MM:SS)", value=default_start_time)
        end_time = st.time_input("End Time (HH:MM:SS)", value=default_end_time)
        video_title = st.text_input('Video Title (optional)')

    if url and (not use_timestamps or (start_time and end_time)):
        output_path = 'videos' 
        os.makedirs(output_path, exist_ok=True)
        filepath = download_video(url, output_path, start_time, end_time, video_title)
        with open(filepath, 'rb') as f:
            st.download_button(
                label='Download video',
                data=f,
                file_name=os.path.basename(filepath)
            )
