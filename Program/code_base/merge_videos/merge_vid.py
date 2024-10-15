from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

def merge_videos(input_dir: str, book_name: str, output_path: str):
    # List and sort video files based on the expected naming convention
    video_files = sorted(
        [
            f for f in os.listdir(input_dir)
            if f.startswith(f"{book_name}") and f.endswith(".mp4")
        ],
        key=lambda x: int(x.split('_')[-1].split('.')[0])
    )

    video_clips = []
    for video_file in video_files:
        video_path = os.path.join(input_dir, video_file)
        try:
            # Load video clip and validate duration
            clip = VideoFileClip(video_path)
            if clip.duration is not None and clip.duration > 0:  # Ensure valid duration
                video_clips.append(clip)
                print(f"Loaded video: {video_file} with duration: {clip.duration} seconds")
            else:
                print(f"Skipping {video_file}: Invalid duration ({clip.duration}).")
                clip.close()  # Close if invalid duration
        except Exception as e:
            print(f"Error loading video {video_file}: {e}. Skipping this file.")

    if not video_clips:
        print("No valid video clips were loaded.")
        return

    try:
        # Concatenate and save the final video
        final_clip = concatenate_videoclips(video_clips, method="compose")
        final_clip.write_videofile(output_path, codec="libx264", audio=False) # audio_codec="aac"
        print(f"Successfully created merged video: {output_path}")
    except Exception as e:
        print(f"Error during concatenation or saving: {e}")
    finally:
        # Close all clips to release resources
        for clip in video_clips:
            clip.close()


#%%
