from moviepy.editor import VideoFileClip, concatenate_videoclips


def merge_videos(videos: list[str], output_path: str) -> None:
    """
    :param videos: list of video file names
    :param output_path: the path of the final video clip
    :return:
    """
    # Load each video clip
    if not videos:
        print("No video files found.")

    else:
        # Creates a list of Video objects from a list of video names
        video_clips = [VideoFileClip(path) for path in videos]

        # Concatenate the video clips into one longer video
        final_clip = concatenate_videoclips(video_clips)

        # Write the final clip to the output file
        final_clip.write_videofile(output_path)

#%%
