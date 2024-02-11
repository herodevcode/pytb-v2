import os
import pytube
from moviepy.editor import VideoFileClip
import streamlit as st
from time import sleep

def download_video(url, output_path, start_minutes, start_seconds, end_minutes, end_seconds, video_title, full_video=False):
    yt = pytube.YouTube(url)
    video = yt.streams.get_highest_resolution()
    temp_output_file = os.path.join(output_path, video.default_filename)
    video.download(output_path=output_path)

    if not full_video:
        # Convert minutes and seconds to total seconds
        start_total_seconds = start_minutes * 60 + start_seconds
        end_total_seconds = end_minutes * 60 + end_seconds

        # Cut the video
        with VideoFileClip(temp_output_file) as video_clip:
            video_segment = video_clip.subclip(start_total_seconds, end_total_seconds)
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

    # Use numeric inputs for minutes and seconds
    col1, col2 = st.columns(2)
    with col1:
        start_minutes = st.number_input("Start Minutes", min_value=0, max_value=99, value=0)
        end_minutes = st.number_input("End Minutes", min_value=0, max_value=99, value=0)
    with col2:
        start_seconds = st.number_input("Start Seconds", min_value=0, max_value=59, value=0)
        end_seconds = st.number_input("End Seconds", min_value=0, max_value=59, value=0)

    video_title = st.text_input('Video Title')
    url = st.text_input('YouTube URL')

    if url and video_title:
        output_path = 'videos'
        os.makedirs(output_path, exist_ok=True)
        with st.status("Processing...", expanded=True) as status:
            st.write("Downloading video...")
            filepath = download_video(url, output_path, start_minutes, start_seconds, end_minutes, end_seconds, video_title, full_video=full_video)
            st.write("Download finished...")
            sleep(1)
            status.update(label="Download complete!", state="complete", expanded=False)
        with open(filepath, 'rb') as f:
            st.download_button(
                label='Download video',
                data=f,
                file_name=os.path.basename(filepath)
            )
