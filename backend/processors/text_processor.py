"""
Text file processor for plain text documents.
"""
from pathlib import Path
from typing import Dict, Any
from backend.utils.logger import processor_logger


class TextProcessor:
    """Simple text file processor."""

    def __init__(self):
        self.logger = processor_logger

    def process(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from plain text file."""
        self.logger.info(f"Processing text file: {file_path.name}")

        result = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_type': 'text',
            'text': '',
            'metadata': {},
            'success': False,
            'error': None
        }

        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            text = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                raise Exception("Could not decode file with any supported encoding")
            
            result['text'] = text
            result['metadata'] = {
                'file_size': file_path.stat().st_size,
                'line_count': len(text.split('\n')),
                'character_count': len(text)
            }
            result['success'] = True

            self.logger.info(f"Successfully processed text file: {file_path.name}")

        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Error processing text file {file_path.name}: {e}")

        return result
