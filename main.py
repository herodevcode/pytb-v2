import os
import pytube
from moviepy.editor import VideoFileClip
import streamlit as st
from datetime import time
from time import sleep

def download_video(url, output_path, start_time, end_time, video_title, full_video=False):
    yt = pytube.YouTube(url)
    video = yt.streams.get_highest_resolution()
    temp_output_file = os.path.join(output_path, video.default_filename)
    video.download(output_path=output_path)

    if not full_video:
        # Correctly convert time objects to total seconds
        start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second

        # Cut the video
        with VideoFileClip(temp_output_file) as video_clip:
            video_segment = video_clip.subclip(start_seconds, end_seconds)
            final_output_filename = f"{video_title}.mp4"
            final_output_file = os.path.join(output_path, final_output_filename)
            video_segment.write_videofile(final_output_file, codec="libx264", audio_codec="aac")
    else:
        # Use the full video as is
        final_output_filename = f"{video_title}.mp4"
        final_output_file = os.path.join(output_path, final_output_filename)
        os.rename(temp_output_file, final_output_file)

    if not full_video:
        os.remove(temp_output_file)  # Remove the original, full-length video
    return final_output_file

if __name__ == '__main__':
    st.title("YouTube Video Downloader")

    full_video = st.checkbox('Download entire video without specifying timestamps')
    
    # Adjusting the default time to support up to 99:59
    default_start_time = time(0, 0)  # Default time interpreted as 0 hours and 0 minutes
    default_end_time = time(0, 0)
    start_time = st.time_input("Start Time (HH:MM:SS)", value=default_start_time)
    end_time = st.time_input("End Time (HH:MM:SS)", value=default_end_time)
    
    video_title = st.text_input('Video Title')
    url = st.text_input('YouTube URL')

    if url and video_title:
        output_path = 'videos'
        os.makedirs(output_path, exist_ok=True)
        with st.status("Processing...", expanded=True) as status:
            st.write("Downloading video...")
            filepath = download_video(url, output_path, start_time, end_time, video_title, full_video=full_video)
            st.write("Download finished...")
            sleep(1)
            status.update(label="Download complete!", state="complete", expanded=False)
        with open(filepath, 'rb') as f:
            st.download_button(
                label='Download video',
                data=f,
                file_name=os.path.basename(filepath)
            )
