import os
import pytube
import streamlit as st
from moviepy.editor import VideoFileClip
from datetime import time

def download_video(url, output_path, start_time, end_time, video_title):
    yt = pytube.YouTube(url)
    video = yt.streams.get_highest_resolution()
    temp_output_file = os.path.join(output_path, video.default_filename)
    video.download(output_path=output_path) 

    # Convert time objects to seconds (treating hours as minutes and minutes as seconds)
    start_seconds = start_time.hour * 60 + start_time.minute
    end_seconds = end_time.hour * 60 + end_time.minute

    # Cut the video
    with VideoFileClip(temp_output_file) as video_clip:
        video_segment = video_clip.subclip(start_seconds, end_seconds)
        final_output_filename = f"{video_title}.mp4"
        final_output_file = os.path.join(output_path, final_output_filename)
        video_segment.write_videofile(final_output_file, codec="libx264", audio_codec="aac")

    os.remove(temp_output_file)  # Remove the original, full-length video
    return final_output_file

if __name__ == '__main__':
    st.title("YouTube Video Downloader")

    default_start_time = time(0, 0)  # Default time interpreted as 0 minutes and 0 seconds
    default_end_time = time(0, 0)
    start_time = st.time_input("Start Time (Minutes:Seconds)", value=default_start_time)
    end_time = st.time_input("End Time (Minutes:Seconds)", value=default_end_time)
    
    video_title = st.text_input('Video Title')

    url = st.text_input('YouTube URL')

    if url and start_time and end_time and video_title:
        output_path = 'videos' 
        os.makedirs(output_path, exist_ok=True)
        filepath = download_video(url, output_path, start_time, end_time, video_title)
        with open(filepath, 'rb') as f:
            st.download_button(
                label='Download video',
                data=f,
                file_name=os.path.basename(filepath)
            )
