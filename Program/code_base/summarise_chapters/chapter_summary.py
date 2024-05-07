from openai import OpenAI
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
import zipfile
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin


def extract_chapter_index(epub_path: str) -> list[str]:
    chapters = []

    with zipfile.ZipFile(epub_path, "r") as zf:
        # Find the rootfile path
        with zf.open("META-INF/container.xml") as container_file:
            soup = BeautifulSoup(container_file, "xml")
            rootfile_path = soup.find("rootfile")["full-path"]

        # Read the .opf file to get the content document(s)
        with zf.open(rootfile_path) as opf_file:
            soup = BeautifulSoup(opf_file, "xml")
            manifest = soup.find("manifest")
            spine = soup.find("spine")
            itemrefs = spine.find_all("itemref")

            # Iterate through itemrefs to find document IDs
            for itemref in itemrefs:
                item_id = itemref["idref"]
                content_item = manifest.find("item", {"id": item_id})

                if (content_item and "media-type" in content_item.attrs
                        and content_item["media-type"] == "application/xhtml+xml"
                ):
                    content_path = content_item["href"]
                    # Adjust for any path differences in the EPUB structure
                    content_full_path = urljoin(
                        os.path.dirname(rootfile_path) + "/", content_path
                    )
                    with zf.open(content_full_path) as content_file:
                        content_soup = BeautifulSoup(content_file, "html.parser")
                        # Example: Extract chapter titles assuming they are in <h1> tags
                        # print(content_soup.text)
                        chapter_titles = content_soup.find_all("part")
                        for title in chapter_titles:
                            chapters.append(title.text)
                        chapters.append(content_soup.text)

    return chapters


def return_chapters(chapter_list: list[str]) -> list[str]:
    book = []
    for chapter in chapter_list:
        if len(chapter) < 1000:
            continue
        else:
            book.append(chapter)
    return book


class ChaptersSummaryAI:
    """This class utilizes the ChatGPT API to automatically generate summaries for chapters within an epub book.

    Attributes:
        book_file_path (str): Path to the epub book file (e.g., "book.epub"). If the file in the same directory, then
                              the name of the book is enough.
        key (str): Your OpenAI API key (requires a positive balance for usage).
    """

    def __init__(self, book_file_path: str, open_ai_key: str):
        self.book_file_path = book_file_path
        self.key = open_ai_key

    def extract_chapters(self):
        # use xml and beautiful soup to extract all different sections of the book
        doc = extract_chapter_index(self.book_file_path)

        # extract the chapters that contain content from all sections
        book = return_chapters(doc)

        return book

    def chapter_summary(self) -> list[str]:
        chapters_summary = []

        client = OpenAI(api_key=self.key)
        chapters = self.extract_chapters()

        for index, chapter in enumerate(chapters):
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "assistant", "content": self.book_file_path + " " + chapter},
                    {"role": "user",
                     "content": f"Create a summary of the {index + 1}-th chapter from the book {self.book_file_path}."
                                f"Provide a concise summary limited to 200 characters for each chapter. Ensure each "
                                f"summary follows the format 'Chapter {index + 1}: summary' Focus solely on the "
                                f"chapter's key points without additional commentary.",
                     },
                ],
            )
            chapters_summary.append(completion.choices[0].message.content)
        return chapters_summary
