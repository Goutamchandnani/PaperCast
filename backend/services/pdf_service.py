import pdfplumber
import os

class PDFService:
    def extract_text(self, file_path: str) -> str:
        """Extract all text from a PDF file."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            raise e
        return text
