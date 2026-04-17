import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import uuid

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    async def process_pdf(self, file_path: str) -> list:
        """Extract text from PDF and split into chunks"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return self._create_chunks(text, file_path)
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    async def process_txt(self, file_path: str) -> list:
        """Extract text from TXT file and split into chunks"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self._create_chunks(text, file_path)
        except Exception as e:
            raise Exception(f"Error processing TXT: {str(e)}")
    
    def _create_chunks(self, text: str, source: str) -> list:
        """Split text into chunks and create Document objects"""
        chunks = self.text_splitter.split_text(text)
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": os.path.basename(source),
                    "chunk_id": i,
                    "doc_id": str(uuid.uuid4())
                }
            )
            documents.append(doc)
        return documents