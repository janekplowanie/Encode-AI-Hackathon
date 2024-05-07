import streamlit as st
import os
from dotenv import load_dotenv
from generate_video.generate_video_from_text import generate_and_download_video
# from merge_videos.merge_vid import merge_videos
from summarise_chapters.chapter_summary import ChaptersSummaryAI


# import merge_videos.merge_vid as m_v
# from m_v import generate_video_from_text
# sys.path.insert(1, "/Users/janrosek/DataspellProjects/Encode-AI-Hackathon/Program/SRC/merge_videos")
# from merge_videos import merge_vid
#
# sys.path.append("/Users/janrosek/DataspellProjects/Encode-AI-Hackathon/Program/SRC/merge_videos")
# from merge_videos import merge_vid

# """
# 1) Upload PDF of book
# 2) PDF sent to chatGPT to summarise chapters of a book
# 3) Each chapter is sent to SD to be turned into an image
# 4) Each image is sent to SVD to be turned into a video
# 5) All videos are then merged together and displayed on the page ???
# """

def main():
    st.markdown(
        """
        <h1 style='text-align: center;'>Moviefy</h1>
        """,
        unsafe_allow_html=True,
    )

    # uploaded_book = st.file_uploader("Upload a book", type=["epub"])
    #
    # print(uploaded_book)
    # st.text(os.getcwd())

    load_dotenv("/Users/janrosek/DataspellProjects/Encode-AI-Hackathon/.env")

    # if not os.path.isfile(".env"):
    #     raise FileNotFoundError(
    #         ".env file not found. Please create a .env file with the required environment variables.")
    #
    # load_dotenv()

    if "STABILITY_API_KEY" not in os.environ:
        raise ValueError("No STABILITY_API_KEY found. Please add your STABILITY_API_KEY to your .env file")

    if "OPEN_AI_KEY" not in os.environ:
        raise ValueError("No OPEN_AI_KEY found. Please add your OPEN_AI_KEY to your .env file")

    stability_api_key = os.getenv("STABILITY_API_KEY")
    open_ai_key = os.getenv("OPEN_AI_KEY")

    uploaded_book = st.file_uploader("Upload a book", type=["epub"])

    # Get the name of the book
    file_name = uploaded_book.name

    st.text(f"{file_name} {type(file_name)}")

    if uploaded_book is not None:
        st.text("File uploaded successfully!")

        output_path_images = f"{file_name}/Images/"
        os.makedirs(output_path_images, exist_ok=True)

        output_path_video = f"{file_name}/Video/"
        os.makedirs(output_path_video, exist_ok=True)

        final_video_path = f"{output_path_video}{file_name}_final_video.mp4"

        with st.spinner("Processing..."):
            # TODO Add video generation

            chapter_summary = ChaptersSummaryAI(file_name, open_ai_key).extract_chapters()
            st.text(chapter_summary[0])
        #     # Should be file_path, we'll see if it works
        #     chapter_summary = ChaptersSummaryAI(file_name, open_ai_key).chapter_summary()
        #
        #     videos = []
        #
        #     # Step 3 and 4
        #     for i, chapter in enumerate(chapter_summary):
        #         image_name = f"Image_{i + 1}"
        #         video_name = f"Video_{i + 1}"
        #         generate_and_download_video(stability_api_key,
        #                                     chapter,
        #                                     output_path_images,
        #                                     output_path_video,
        #                                     image_name,
        #                                     video_name,
        #                                     cfg_scale=1.8,
        #                                     motion_bucket_id=127)
        #
        #         videos.append(f"{output_path_video}{video_name}")
        #
        #     # Step 5
        #     merge_videos(videos, final_video_path)
        #
        # with open(final_video_path, "rb") as video_file:
        #     video_bytes = video_file.read()
        #
        # st.subheader("Processed Video:")
        # st.video(video_bytes)


if __name__ == "__main__":
    main()
