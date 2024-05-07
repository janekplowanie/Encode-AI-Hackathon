from Splite_book import *
from openai import OpenAI


class ChaptersSummaryAI:
    """Make summary for the book by chapters with ChatGPT API.

    Attributes:
        book_file        Path to the book of pdf format (e.g. "book.pdf")
        chapters_pages   Pages of chapters [(start_page, end_page)] (e.g. [(1,7),(8,13),(14,18)])
        key              OpenAI Key for access to ChatGPT API (requires positive balance for API usage)
    """

    def __init__(self, book_file: str, key: str):
        self.book_file = book_file
        self.key = key

    def extract_chapters(self):
        ####use xml and beautiful soup to extract all different sections of the book
        doc = extract_chapter_index(self.book_file)
        ##extract the chapters that contain content from all sections
        book = return_chapters(doc)

        return book

    def ChapterSummary(self):
        chapters_summary = []
        i = 0
        client = OpenAI(api_key=self.key)
        book = self.extract_chapters()

        for chapter in book:
            i += 1
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "assistant", "content": self.book_file + " " + chapter},
                    {
                        "role": "user",
                        "content": f"Create a summary of the {i}-th chapter from the book '{self.book_file}'. Provide a concise summary limited to 200 characters for each chapter. Ensure each summary follows the format 'Chapter {i}: summary' Focus solely on the chapter's key points without additional commentary.",
                    },
                ],
            )
            chapters_summary.append(completion.choices[0].message.content)
        return chapters_summary
