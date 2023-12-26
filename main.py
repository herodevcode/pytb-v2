import os
import pytube
import streamlit as st
from moviepy.editor import VideoFileClip
from datetime import time, timedelta

## pip install -r requirements.txt
## streamlit run main.py

def time_to_seconds(time_obj):
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second



def download_video(url, output_path, start_time=None, end_time=None, video_title=None):
    yt = pytube.YouTube(url)
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    
    if video_title is None:
        video_title = yt.title.replace('/', '_').replace('\\', '_')  # Replace invalid filename characters
    final_output_filename = f"{video_title}.mp4"
    final_output_file = os.path.join(output_path, final_output_filename)

    temp_output_file = os.path.join(output_path, video.default_filename)
    video.download(output_path=output_path) 

    if start_time is not None and end_time is not None:
        # Convert time objects to seconds
        start_seconds = time_to_seconds(start_time)
        end_seconds = time_to_seconds(end_time)

        # Load the video clip to get its duration and ensure we're within bounds
        with VideoFileClip(temp_output_file) as video_clip:
            if start_seconds < 0 or end_seconds < 0:
                raise ValueError("Start time and end time must be positive.")
            if start_seconds >= video_clip.duration or end_seconds > video_clip.duration:
                raise ValueError("Start time and end time must be within the video duration.")
            if start_seconds >= end_seconds:
                raise ValueError("Start time must be less than end time.")

            video_segment = video_clip.subclip(start_seconds, end_seconds)
            video_segment.write_videofile(final_output_file, codec="libx264", audio_codec="aac")

        os.remove(temp_output_file)  # Remove the original, full-length video
    else:
        # If no start and end times are provided, simply move the downloaded file to the final destination
        os.rename(temp_output_file, final_output_file)

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
        start_seconds = time_to_seconds(start_time)
        end_seconds = time_to_seconds(end_time)
    
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
