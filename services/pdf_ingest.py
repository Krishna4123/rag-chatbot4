"""
PDF text extraction service
Handles PDF file processing and text extraction
"""

import os
import logging
import re
from pypdf import PdfReader
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and processing"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']

    def _clean_extracted_text(self, text: str) -> str:
        """
        Apply immediate cleaning to text extracted from PDF.
        This handles common PDF extraction artifacts like hyphens, ligatures, and excessive spaces.
        """
        # Remove common ligatures (fi, fl, etc.) which often appear as single chars or weird symbols
        text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
        
        # Replace multiple newlines with a single one (or space, depending on desired paragraph separation)
        text = re.sub(r'\n\s*\n', '\n', text) # Collapse multiple newlines
        
        # Remove hyphenation at line breaks - simple heuristic
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text) 
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove null characters
        text = text.replace("\u0000", "")
        
        return text
    
    def extract_text(self, filepath: str) -> Optional[str]:
        """
        Extract text from PDF file
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            text_content = ""
            with open(filepath, 'rb') as file:
                pdf_reader = PdfReader(file) # Use pypdf.PdfReader
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            cleaned_page_text = self._clean_extracted_text(page_text)
                            text_content += f"\n--- Page {page_num + 1} ---\n"
                            text_content += cleaned_page_text
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1} of {filepath}: {e}")
                        continue
            
            return text_content.strip() if text_content else None
            
        except Exception as e:
            logger.error(f"Error processing PDF {filepath}: {e}")
            return None
    
    def extract_metadata(self, filepath: str) -> Dict[str, any]:
        """
        Extract metadata from PDF file
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            metadata = {
                'filename': os.path.basename(filepath),
                'filepath': filepath,
                'pages': 0,
                'title': '',
                'author': '',
                'subject': '',
                'creator': ''
            }
            
            with open(filepath, 'rb') as file:
                pdf_reader = PdfReader(file) # Use pypdf.PdfReader
                metadata['pages'] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    metadata['title'] = pdf_reader.metadata.get('/Title', '')
                    metadata['author'] = pdf_reader.metadata.get('/Author', '')
                    metadata['subject'] = pdf_reader.metadata.get('/Subject', '')
                    metadata['creator'] = pdf_reader.metadata.get('/Creator', '')
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {filepath}: {e}")
            return {'filename': os.path.basename(filepath), 'error': str(e)}
    
    def process_directory(self, directory_path: str) -> List[Dict[str, any]]:
        """
        Process all PDF files in a directory
        
        Args:
            directory_path: Path to directory containing PDFs
            
        Returns:
            List of processed PDF data
        """
        results = []
        
        if not os.path.exists(directory_path):
            return results
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join(directory_path, filename)
                text = self.extract_text(filepath)
                metadata = self.extract_metadata(filepath)
                
                if text:
                    results.append({
                        'filename': filename,
                        'text': text,
                        'metadata': metadata
                    })
        
        return results
    
    def is_valid_pdf(self, filepath: str) -> bool:
        """
        Check if file is a valid PDF
        
        Args:
            filepath: Path to the file
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            with open(filepath, 'rb') as file:
                PdfReader(file) # Use pypdf.PdfReader
            return True
        except:
            return False
