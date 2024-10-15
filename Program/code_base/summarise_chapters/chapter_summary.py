import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import openai
from typing import List
import os
import streamlit as st


def extract_story_content_v2(epub_path: str) -> list[str]:
    """
    Extracts the story content from an EPUB file, ignoring publishing and metadata files.

    Args:
        epub_path (str): Path to the EPUB file.

    Returns:
        list[str]: List of chapter texts extracted from the EPUB.
    """
    chapters = []

    with zipfile.ZipFile(epub_path, "r") as zf:
        # Identify the root .opf file
        with zf.open("META-INF/container.xml") as container_file:
            soup = BeautifulSoup(container_file, "xml")
            rootfile_path = soup.find("rootfile")["full-path"]

        # Read the .opf file to locate the spine (reading order of chapters)
        with zf.open(rootfile_path) as opf_file:
            soup = BeautifulSoup(opf_file, "xml")
            manifest = {item["id"]: item["href"] for item in soup.find_all("item")}
            spine = soup.find("spine")
            itemrefs = [itemref["idref"] for itemref in spine.find_all("itemref")]

            # Iterate through spine items (in order) to extract chapter content
            for item_id in itemrefs:
                if item_id in manifest:
                    content_path = urljoin(rootfile_path, manifest[item_id])

                    # Check if the chapter file exists and attempt to read it
                    try:
                        with zf.open(content_path) as content_file:
                            content_soup = BeautifulSoup(content_file, "html.parser")
                            chapter_text = content_soup.get_text(separator="\n", strip=True)
                            chapters.append(chapter_text)
                    except KeyError:
                        print(f"Error reading {content_path}: file not found in EPUB archive.")

    return chapters


class ChaptersSummaryAI:
    """
    This class utilizes the ChatGPT API to generate descriptive summaries for chapters within an EPUB book.

    Attributes:
        book_file_path (str): Path to the EPUB book file.
        key (str): OpenAI API key.
    """

    def __init__(self, book_file_path: str, open_ai_key: str):
        self.book_file_path = book_file_path
        self.key = open_ai_key
        # openai.api_key = open_ai_key  # Set the API key
        self.client = openai.OpenAI(api_key=open_ai_key)

    def extract_chapters(self) -> List[str]:
        """
        Extracts chapters from the EPUB file.

        Returns:
            List[str]: List of extracted chapter texts.
        """
        chapters = extract_story_content_v2(self.book_file_path)
        return chapters

    def summarize_chapters(self) -> List[str]:
        """
        Summarizes each chapter by passing it to the OpenAI API with a descriptive prompt.

        Returns:
            List[str]: List of descriptive summaries for each chapter.
        """
        chapters_summary = []
        chapters = self.extract_chapters()

        # Streamlit progress bar
        # progress_bar = st.progress(0)

        for index, chapter in enumerate(chapters):
            try:
                completion = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Use the correct model here gpt-4o gpt-3.5-turbo
                    messages=[
                        {"role": "system",
                         "content": "You are an assistant that creates visual and immersive summaries for chapters in novels. These summaries are then used to generate images."},
                        {"role": "user",
                         "content": f"Create a descriptive, visual summary for Chapter {index + 1} of a fictional book, based on the following content:\n\n{chapter}\n\n "
                                    f"Focus on the imagery, key scenes, characters, and setting details, making it as vivid and story-like as possible. Don't make up information, generate decriptions only on what's in the book content you received "
                                    f"Ignore any publishing information, prologues, forewords, or acknowledgments. "
                                    f"Limit to 200 characters for each chapter. Don't add Chapter and number at the begining of every summary as there's a script that already formats it that way"   # , and format as 'Chapter {index + 1}: [summary]'.
                         }
                    ]
                )
                summary = completion.choices[0].message.content
                chapters_summary.append(f"Chapter {index + 1}: {summary}")

            except Exception as e:
                # st.error(f"Error summarizing Chapter {index + 1}: {e}")
                chapters_summary.append(f"Chapter {index + 1}: Error in summarization: {e}")

            # Update progress bar
            # progress_bar.progress((index + 1) / len(chapters))

        return chapters_summary


#=============================================================================
#
# def extract_story_content(epub_path: str) -> list[str]:
#     """
#     Extracts only the main story content from an EPUB file, ignoring publishing details.
#
#     Args:
#         epub_path (str): Path to the EPUB file.
#
#     Returns:
#         list[str]: List of chapter texts or main story segments.
#     """
#     chapters = []
#
#     with zipfile.ZipFile(epub_path, "r") as zf:
#         # Locate the root .opf file path
#         try:
#             with zf.open("META-INF/container.xml") as container_file:
#                 container_soup = BeautifulSoup(container_file, "xml")
#                 rootfile_path = container_soup.find("rootfile")["full-path"]
#         except Exception as e:
#             print(f"Error finding rootfile: {e}")
#             return []
#
#         # Parse the .opf file to locate content documents
#         with zf.open(rootfile_path) as opf_file:
#             opf_soup = BeautifulSoup(opf_file, "xml")
#             manifest = {item['id']: item['href'] for item in opf_soup.find_all("item")}
#             spine_ids = [itemref["idref"] for itemref in opf_soup.find("spine").find_all("itemref")]
#
#             # Iterate through spine IDs to retrieve story content
#             for item_id in spine_ids:
#                 content_path = manifest.get(item_id)
#                 if not content_path:
#                     continue
#
#                 # Adjust for nested paths within the EPUB structure
#                 content_full_path = urljoin(os.path.dirname(rootfile_path) + "/", content_path)
#
#                 try:
#                     with zf.open(content_full_path) as content_file:
#                         content_soup = BeautifulSoup(content_file, "html.parser")
#                         # Only retrieve text within headers and paragraph tags
#                         chapter_text = "\n".join(tag.get_text() for tag in content_soup.find_all(['h1', 'h2', 'p']))
#
#                         # Append non-empty chapters to our list
#                         if chapter_text.strip():
#                             chapters.append(chapter_text)
#                 except Exception as e:
#                     print(f"Error reading {content_full_path}: {e}")
#
#     return chapters


# def extract_chapter_index(epub_path: str) -> list[str]:
#     chapters = []
#
#     with zipfile.ZipFile(epub_path, "r") as zf:
#         # Find the root file path
#         with zf.open("META-INF/container.xml") as container_file:
#             soup = BeautifulSoup(container_file, "xml")
#             rootfile_path = soup.find("rootfile")["full-path"]
#
#         # Read the .opf file to get the content document(s)
#         with zf.open(rootfile_path) as opf_file:
#             soup = BeautifulSoup(opf_file, "xml")
#             manifest = soup.find("manifest")
#             spine = soup.find("spine")
#             itemrefs = spine.find_all("itemref")
#
#             # Iterate through itemrefs to find document IDs
#             for itemref in itemrefs:
#                 item_id = itemref["idref"]
#                 content_item = manifest.find("item", {"id": item_id})
#
#                 if (content_item and "media-type" in content_item.attrs
#                         and content_item["media-type"] == "application/xhtml+xml"
#                 ):
#                     content_path = content_item["href"]
#                     # Adjust for any path differences in the EPUB structure
#                     content_full_path = urljoin(
#                         os.path.dirname(rootfile_path) + "/", content_path
#                     )
#                     with zf.open(content_full_path) as content_file:
#                         content_soup = BeautifulSoup(content_file, "html.parser")
#                         # Example: Extract chapter titles assuming they are in <h1> tags
#                         # print(content_soup.text)
#                         chapter_titles = content_soup.find_all("part")
#                         for title in chapter_titles:
#                             chapters.append(title.text)
#                         chapters.append(content_soup.text)
#
#     return chapters

#
# def return_chapters(chapter_list: list[str]) -> list[str]:
#     book = []
#     for chapter in chapter_list:
#         if len(chapter) < 1000:
#             continue
#         else:
#             book.append(chapter)
#     return book
#
#
# class ChaptersSummaryAI:
#     """This class utilizes the ChatGPT API to automatically generate summaries for chapters within an epub book.
#
#     Attributes:
#         book_file_path (str): Path to the epub book file (e.g., "book.epub"). If the file in the same directory, then
#                               the name of the book is enough.
#         key (str): Your OpenAI API key (requires a positive balance for usage).
#     """
#
#     def __init__(self, book_file_path: str, open_ai_key: str):
#         self.book_file_path = book_file_path
#         self.key = open_ai_key
#
#     def extract_chapters(self):
#         # use xml and beautiful soup to extract all different sections of the book
#         doc = extract_chapter_index(self.book_file_path)
#
#         # extract the chapters that contain content from all sections
#         book = return_chapters(doc)
#
#         return book
#
#     def chapter_summary(self) -> list[str]:
#         chapters_summary = []
#
#         client = OpenAI(api_key=self.key)
#         chapters = self.extract_chapters()
#
#         for index, chapter in enumerate(chapters):
#             completion = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "assistant", "content": self.book_file_path + " " + chapter},
#                     {"role": "user",
#                      "content": f"Create a summary of the {index + 1}-th chapter from the book {self.book_file_path}."
#                                 f"Provide a concise summary limited to 200 characters for each chapter. Ensure each "
#                                 f"summary follows the format 'Chapter {index + 1}: summary' Focus solely on the "
#                                 f"chapter's key points without additional commentary.",
#                      },
#                 ],
#             )
#             chapters_summary.append(completion.choices[0].message.content)
#         return chapters_summary

#
# if __name__ == "__main__":
#     file_name = "/Users/qiqi/hackathon/Encode-AI-Hackathon/chapteriser/blyton-five-fall-into-adventure.epub"
#     filename = "/Users/qiqi/hackathon/Encode-AI-Hackathon/chapteriser/George Orwell - Animal Farm-Amazon Classics (2021).epub"
#     pdffile = "/Users/qiqi/hackathon/Encode-AI-Hackathon/orwellanimalfarm.pdf"
#     epub_path = "path/to/your/book.epub"
#     chapter_list = extract_chapter_index(file_name)
#     print(len(chapter_list[3]))
#     book = []
#     for chapter in chapter_list:
#         if len(chapter) < 1000:
#             continue
#         else:
#             book.append(chapter)
#     print(len(book))
#     # chapters = chapter_index.split('Chapter')
#     # print(chapters)

#%%
