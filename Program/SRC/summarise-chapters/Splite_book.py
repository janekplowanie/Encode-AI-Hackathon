from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
import zipfile
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin


def extract_chapter_index(epub_path):
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
                if (
                    content_item
                    and "media-type" in content_item.attrs
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


# Example usage


def return_chapters(chapter_list):
    book = []
    for chapter in chapter_list:
        if len(chapter) < 1000:
            continue
        else:
            book.append(chapter)
    return book


if __name__ == "__main__":
    file_name = "/Users/qiqi/hackathon/Encode-AI-Hackathon/chapteriser/blyton-five-fall-into-adventure.epub"
    filename = "/Users/qiqi/hackathon/Encode-AI-Hackathon/chapteriser/George Orwell - Animal Farm-Amazon Classics (2021).epub"
    pdffile = "/Users/qiqi/hackathon/Encode-AI-Hackathon/orwellanimalfarm.pdf"
    epub_path = "path/to/your/book.epub"
    chapter_list = extract_chapter_index(file_name)
    print(len(chapter_list[3]))
    book = []
    for chapter in chapter_list:
        if len(chapter) < 1000:
            continue
        else:
            book.append(chapter)
    print(len(book))
    # chapters = chapter_index.split('Chapter')
    # print(chapters)
