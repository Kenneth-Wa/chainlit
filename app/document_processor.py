import os
import glob
from app.utils.index import FAISSIndex

from app.constants import PDF_DIR, INDEX_DIR
from app.build_index import create_faiss_index

from app.find_context import find_context
from app.utils.oai import CustomEndpoint

class DocumentProcessor:
    def __init__(self):
        self.index_path = INDEX_DIR
        if not os.path.exists(self.index_path):
            os.makedirs(self.index_path)

    async def query(self, text):
        # Ensure there's a PDF file to index
        pdf_files = glob.glob(os.path.join(PDF_DIR, '**', '*.pdf'), recursive=True)
        
        if not pdf_files:
            raise FileNotFoundError("No PDF files available for indexing.")

        # Assuming you're indexing all available PDFs and using the first one for now
        pdf_path = pdf_files[0]

        # Create the index if it doesn't exist
        new_index_path = create_faiss_index(pdf_path)

        prompt, snippets = find_context(text, new_index_path)
    
        max_completion_tokens = int(os.environ.get("MAX_COMPLETION_TOKENS"))

        chat = CustomEndpoint()
        stream = chat.generate(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_completion_tokens,
        )

        return stream