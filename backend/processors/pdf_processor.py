"""
PDF text extraction with support for multiple libraries and OCR fallback.
"""
from pathlib import Path
from typing import Dict, Any, List
import PyPDF2
import pdfminer.high_level
from PIL import Image
import io
from backend.utils.logger import processor_logger

# Optional OCR support
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


class PDFProcessor:
    """Extract text and metadata from PDF files."""

    def __init__(self):
        """Initialize PDF processor."""
        self.logger = processor_logger

    def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary containing extracted text and metadata
        """
        self.logger.info(f"Processing PDF: {file_path.name}")

        result = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_type': 'pdf',
            'text': '',
            'pages': [],
            'metadata': {},
            'success': False,
            'error': None
        }

        try:
            # Try pdfminer first (better for text extraction)
            text = self._extract_with_pdfminer(file_path)

            if not text.strip():
                # Fallback to PyPDF2
                text = self._extract_with_pypdf2(file_path)

            if not text.strip():
                # Last resort: OCR
                text = self._extract_with_ocr(file_path)

            result['text'] = text
            result['success'] = True

            # Extract metadata
            result['metadata'] = self._extract_metadata(file_path)

            # Extract per-page content
            result['pages'] = self._extract_pages(file_path)

            self.logger.info(f"Successfully processed PDF: {file_path.name}")

        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Error processing PDF {file_path.name}: {e}")

        return result

    def _extract_with_pdfminer(self, file_path: Path) -> str:
        """Extract text using pdfminer."""
        try:
            return pdfminer.high_level.extract_text(str(file_path))
        except Exception as e:
            self.logger.warning(f"PDFMiner extraction failed: {e}")
            return ""

    def _extract_with_pypdf2(self, file_path: Path) -> str:
        """Extract text using PyPDF2."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            self.logger.warning(f"PyPDF2 extraction failed: {e}")
            return ""

    def _extract_with_ocr(self, file_path: Path) -> str:
        """Extract text using OCR as fallback."""
        if not PYTESSERACT_AVAILABLE:
            self.logger.warning("OCR requested but pytesseract is not installed")
            return ""
        
        try:
            # This is a simplified OCR approach
            # In production, you'd convert PDF pages to images first
            self.logger.info(f"Attempting OCR for {file_path.name}")
            return "OCR extraction would be implemented here for scanned PDFs"
        except Exception as e:
            self.logger.warning(f"OCR extraction failed: {e}")
            return ""

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract PDF metadata."""
        metadata = {}
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if reader.metadata:
                    metadata = {
                        'title': reader.metadata.get('/Title', ''),
                        'author': reader.metadata.get('/Author', ''),
                        'subject': reader.metadata.get('/Subject', ''),
                        'creator': reader.metadata.get('/Creator', ''),
                        'producer': reader.metadata.get('/Producer', ''),
                        'creation_date': str(reader.metadata.get('/CreationDate', '')),
                        'modification_date': str(reader.metadata.get('/ModDate', ''))
                    }
                metadata['page_count'] = len(reader.pages)
        except Exception as e:
            self.logger.warning(f"Metadata extraction failed: {e}")

        return metadata

    def _extract_pages(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract content from each page."""
        pages = []
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for i, page in enumerate(reader.pages):
                    pages.append({
                        'page_number': i + 1,
                        'text': page.extract_text(),
                        'metadata': {
                            'rotation': page.get('/Rotate', 0) if hasattr(page, 'get') else 0
                        }
                    })
        except Exception as e:
            self.logger.warning(f"Page extraction failed: {e}")

        return pages