"""
PDF text extraction service
Handles PDF file processing and text extraction
"""

import os
import PyPDF2
from typing import List, Dict, Optional

class PDFProcessor:
    """Handles PDF text extraction and processing"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text(self, filepath: str) -> Optional[str]:
        """
        Extract text from PDF file
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            text = ""
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text
                    except Exception as e:
                        print(f"Error extracting page {page_num + 1}: {e}")
                        continue
            
            return text.strip() if text else None
            
        except Exception as e:
            print(f"Error processing PDF {filepath}: {e}")
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
                pdf_reader = PyPDF2.PdfReader(file)
                metadata['pages'] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    metadata['title'] = pdf_reader.metadata.get('/Title', '')
                    metadata['author'] = pdf_reader.metadata.get('/Author', '')
                    metadata['subject'] = pdf_reader.metadata.get('/Subject', '')
                    metadata['creator'] = pdf_reader.metadata.get('/Creator', '')
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting metadata from {filepath}: {e}")
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
                PyPDF2.PdfReader(file)
            return True
        except:
            return False
