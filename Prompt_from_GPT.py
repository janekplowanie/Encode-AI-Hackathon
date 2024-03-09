from openai import OpenAI
from chapteriser.Splite_book import *
class ChaptersSummaryAI:
    """Make summary for book by chapters with ChatGPT API.

    Attributes:
        book_file        Path to book of pdf format (e.g. "book.pdf")
        chapters_pages   Pages of chapters [(start_page, end_page)] (e.g. [(1,7),(8,13),(14,18)])
        key              OpenAI Key for access to ChatGPT API (requires positive balance for API usage)
    """
    def __init__(self, book_file : str,  key : str):
        self.book_file=book_file
        self.key=key
    def extract_chapters(self):
        ####use xml and beautiful soup to extract all different sections of the book
        doc =  extract_chapter_index(self.book_file)
        ##extract the chapters that contain content from all sections
        book = return_chapters(doc)
  
        return book
    
    def ChapterSummary(self):
        chapters_summary=[]
        i=0
        client = OpenAI(api_key=self.key)
        book=self.extract_chapters()
        
        for chapter in book:
            i+=1
            completion = client.chat.completions.create(
              model="gpt-3.5-turbo",
              messages=[
                  {"role": "assistant", "content": self.book_file + ' ' + chapter},
                  {"role": "user", "content": f"Make a summary of the {i}-th chapter of the book {self.book_file}. Please just give the summary without saying anything else."}
              ]
            )
            chapters_summary.append(completion.choices[0].message.content)
        return chapters_summary