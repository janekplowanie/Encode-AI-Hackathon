import streamlit as st
from chapter_summary import *
from sd_functions import *
from dotenv import load_dotenv
import tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips

# This file is a copy of synopsis.py but it's simplified to serve as a DEMO
def main():

    load_dotenv()

    st.markdown(
        """
        <h1 style='text-align: center;'>Synopsis AI</h1>
        """,
        unsafe_allow_html=True,
    )

    sd_api_key = "sk-bkuIqt0pQzG17G7H3q8phhkvYLBkUK3S7z4vqMfLtCdEjkDJ"
    api_key = "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"

    def merge_videos(videos, output_path):
        # Load each video clip
        # if not videos:
        #     print("No video files found.")
        # return
        video_clips = [VideoFileClip(path) for path in videos]

        # Concatenate the video clips into one longer video
        final_clip = concatenate_videoclips(video_clips)

        # Write the final clip to the output file
        final_clip.write_videofile(output_path)

    def get_files_in_directory(directory_path):
        files = []
        # Iterate over all the files in the directory
        for file_name in os.listdir(directory_path):
            # Check if the file is a regular file (not a directory)
            if os.path.isfile(os.path.join(directory_path, file_name)):
                # Add the file to the list
                files.append(os.path.join(directory_path, file_name))
        return files

    if not api_key:
        st.error("Please set the API_KEY environment variable.")

    else:
        uploaded_book = st.file_uploader("Upload a book", type=["epub"])

        print(uploaded_book)
        if uploaded_book is not None:
            st.text("File uploaded successfully!")

            # Save the uploaded file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_book.getvalue())

                # Get the path of the temporary file
                file_path = tmp_file.name

            # Placeholder for backend processing (simulated with time.sleep)
            with st.spinner("Processing..."):
                time.sleep(10)

            #     out = ChaptersSummaryAI(file_path, api_key).ChapterSummary()
            #     # Send each chapter summary to SD to get videos
            #     # videos = get_files_in_directory(
            #     #     # "C:\\Users\\roman\\Projects\\synopsis-app\\book\\Videos"
            #     #     "/mnt/c/Users/t/Documents/GIT/Encode-AI-Hackathon/synopsis-app/book/Videos"
            #     # )

            #     videos = []
            #     counter = 0
            #     current_datetime = time.strftime("%Y%m%d-%H%M%S")
            #     videos_list_path = f"book/Videos_{current_datetime}" 
            #     for prompt in out:
            #         print(prompt)
            #         video = generate_and_download_video(
            #             videos_list_path, sd_api_key, prompt, "book", cfg_scale=5, motion_bucket_id=200
            #         )
            #         videos.append(video)
            #         counter += 1
            #         if counter == 2:
            #             break

                       
            #     # Stitch videos together
            #     print("video path:", videos)
            #     current_datetime = time.strftime("%Y%m%d-%H%M%S")
            #     output = f"/mnt/c/Users/t/Documents/GIT/Encode-AI-Hackathon/synopsis-app/book/merged_video_{current_datetime}.mp4"
            #     merge_videos(videos, output_path=output)

            # Display video
            st.subheader("Processed Video:")
            # st.video(output)
            demo_output = "/mnt/c/Users/t/Documents/GIT/Encode-AI-Hackathon/synopsis-app/book/merged_video.mp4"
            st.video(demo_output)

    # """
    # 1) Upload PDF of book 
    # 2) PDF sent to chatGPT to summarise chapters of a book
    # 3) Each chapter is sent to SD to be turned into an image
    # 4) Each image is sent to SVD to be turned into a video
    # 5) All videos are then merged together and displayed on the page ???
    # """


if __name__ == "__main__":
    main()
