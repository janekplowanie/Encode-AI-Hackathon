# Moviefy_app.py
# Moviefy_app.py

import os
import streamlit as st
from dotenv import load_dotenv
from summarise_chapters.chapter_summary import ChaptersSummaryAI
from generate_video.generate_video_from_text import generate_and_download_video
from merge_videos.merge_vid import merge_videos

def main():
    # Load API keys from environment variables
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    stability_key = os.getenv("STABILITY_API_KEY")

    # Streamlit App Interface
    st.title("Moviefy: Turn Your Book into a Visual Story")

    # EPUB Upload
    uploaded_file = st.file_uploader("Upload an EPUB file", type="epub")

    if uploaded_file is not None:

        # Step 0: Prepare the directories
        INPUT_BOOK_FOLDER = "input_book"
        os.makedirs(INPUT_BOOK_FOLDER, exist_ok=True)

        book_name = uploaded_file.name
        book_path = os.path.join(INPUT_BOOK_FOLDER, book_name)

        # Save the uploaded file to the "input_book" folder
        with open(book_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("EPUB file uploaded and saved successfully!")

        # Images and Videos saved in the directory of a particular book
        OUTPUT_IMAGES_FOLDER = f"output_image_video/{book_name}/Images/"
        OUTPUT_VIDEOS_FOLDER = f"output_image_video/{book_name}/Videos/"
        OUTPUT_MERGED_VIDEO_FOLDER = f"output_image_video/{book_name}/Merged_videos/"

        os.makedirs(OUTPUT_IMAGES_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_VIDEOS_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_MERGED_VIDEO_FOLDER, exist_ok=True)

        # Step 1: Extract chapters and summarize
        st.write("**Extracting and summarizing chapters...**")
        summarizer = ChaptersSummaryAI(book_file_path=book_path, open_ai_key=openai_key)
        chapter_summaries = summarizer.summarize_chapters()
        st.write("Summaries generated for each chapter!")

        # Step 2: Generate images and videos from summaries
        st.write("**Generating images and videos from summaries...**")
        cfg_scale = st.slider("CFG Scale (1 to 10)", 1, 10, 5)
        motion_bucket_id = st.slider("Motion Bucket ID (1 to 255)", 1, 255, 50)
        book_name = os.path.splitext(uploaded_file.name)[0]

        for index, summary in enumerate(chapter_summaries):
            chapter_name = f"{book_name}_chapter_{index + 1}"
            try:
                # Generate and download video for each summary
                generate_and_download_video(
                    stability_api_key=stability_key,
                    text_prompts=summary,
                    book_name=chapter_name,
                    output_path_images=OUTPUT_IMAGES_FOLDER,
                    output_path_video=OUTPUT_VIDEOS_FOLDER,
                    cfg_scale=cfg_scale,
                    motion_bucket_id=motion_bucket_id
                )
                st.write(f"Generated video for {chapter_name}")
            except Exception as e:
                st.error(f"Error generating video for {chapter_name}: {e}")

        # Step 3: Merge videos into a single video
        st.write("**Merging all chapter videos into a final video...**")
        output_merged_video_path = os.path.join(OUTPUT_MERGED_VIDEO_FOLDER, f"{book_name}_final_video.mp4")

        merge_videos(
            input_dir=OUTPUT_VIDEOS_FOLDER,
            book_name=book_name,
            output_path=output_merged_video_path
        )

        # Display the final video if merging was successful
        if os.path.exists(output_merged_video_path):
            st.write("**Final video created!**")
            st.video(output_merged_video_path)
        else:
            st.error("Failed to create the final video.")

# Run the app
if __name__ == "__main__":
    main()


# import streamlit as st
# import os
# from dotenv import load_dotenv
# from summarise_chapters.chapter_summary import ChaptersSummaryAI
# from generate_video.generate_video_from_text import generate_and_download_video
# from merge_videos.merge_vid import merge_videos
#
#
# # import merge_videos.merge_vid as m_v
# # from m_v import generate_video_from_text
# # sys.path.insert(1, "/Users/janrosek/DataspellProjects/Encode-AI-Hackathon/Program/SRC/merge_videos")
# # from merge_videos import merge_vid
# #
# # sys.path.append("/Users/janrosek/DataspellProjects/Encode-AI-Hackathon/Program/SRC/merge_videos")
# # from merge_videos import merge_vid
#
# # """
# # 1) Upload PDF of book
# # 2) PDF sent to chatGPT to summarise chapters of a book
# # 3) Each chapter is sent to SD to be turned into an image
# # 4) Each image is sent to SVD to be turned into a video
# # 5) All videos are then merged together and displayed on the page ???
# # """
#
# def main():
#     st.markdown(
#         """
#         <h1 style='text-align: center;'>Moviefy</h1>
#         """,
#         unsafe_allow_html=True,
#     )
#
#     uploaded_book = st.file_uploader("Upload a book", type=["epub"])
#
#     print(uploaded_book)
#     st.text(os.getcwd())
#
#     # load_dotenv("/Users/janrosek/DataspellProjects/Encode-AI-Hackathon/.env")
#
#     if not os.path.isfile(".env"):
#         raise FileNotFoundError(
#             ".env file not found. Please create a .env file with the required environment variables.")
#
#     load_dotenv()
#
#     if "STABILITY_API_KEY" not in os.environ:
#         raise ValueError("No STABILITY_API_KEY found. Please add your STABILITY_API_KEY to your .env file")
#
#     if "OPENAI_API_KEY" not in os.environ:
#         raise ValueError("No OPENAI_API_KEY found. Please add your OPENAI_API_KEY to your .env file")
#
#     stability_api_key = os.getenv("STABILITY_API_KEY")
#     open_ai_key = os.getenv("OPENAI_API_KEY")
#
#     uploaded_book = st.file_uploader("Upload a book", type=["epub"])
#
#     # Get the name of the book
#     file_name = uploaded_book.name
#
#     st.text(f"{file_name} {type(file_name)}")
#
#     if uploaded_book is not None:
#         st.text("File uploaded successfully!")
#
#         output_path_images = f"{file_name}/Images/"
#         os.makedirs(output_path_images, exist_ok=True)
#
#         output_path_video = f"{file_name}/Video/"
#         os.makedirs(output_path_video, exist_ok=True)
#
#         final_video_path = f"{output_path_video}{file_name}_final_video.mp4"
#
#         with st.spinner("Processing..."):
#             # TODO Add video generation
#
#             chapter_summary = ChaptersSummaryAI(file_name, open_ai_key).extract_chapters()
#             st.text(chapter_summary[0])
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
#
#
# if __name__ == "__main__":
#     main()
