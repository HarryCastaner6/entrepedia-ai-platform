"""
Image OCR processing for text extraction from images.
"""
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image, ImageEnhance, ImageFilter
from backend.utils.logger import processor_logger

# Optional OCR dependencies
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class ImageProcessor:
    """Extract text from images using OCR."""

    def __init__(self):
        """Initialize image processor."""
        self.logger = processor_logger
        self.easyocr_reader = None

    def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from image using OCR.

        Args:
            file_path: Path to image file

        Returns:
            Dictionary containing extracted text and metadata
        """
        self.logger.info(f"Processing image: {file_path.name}")

        result = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_type': 'image',
            'text': '',
            'ocr_results': [],
            'metadata': {},
            'success': False,
            'error': None
        }

        try:
            # Load and preprocess image
            image = Image.open(file_path)
            processed_image = self._preprocess_image(image)

            # Try multiple OCR engines
            text_results = []

            # Method 1: Tesseract
            if PYTESSERACT_AVAILABLE:
                try:
                    tesseract_text = self._extract_with_tesseract(processed_image)
                    if tesseract_text.strip():
                        text_results.append({
                            'engine': 'tesseract',
                            'text': tesseract_text,
                            'confidence': self._get_tesseract_confidence(processed_image)
                        })
                except Exception as e:
                    self.logger.warning(f"Tesseract OCR failed: {e}")

            # Method 2: EasyOCR
            if EASYOCR_AVAILABLE:
                try:
                    easyocr_text = self._extract_with_easyocr(file_path)
                    if easyocr_text.strip():
                        text_results.append({
                            'engine': 'easyocr',
                            'text': easyocr_text,
                            'confidence': None
                        })
                except Exception as e:
                    self.logger.warning(f"EasyOCR failed: {e}")

            # If no OCR available, note that in the text
            if not text_results and not PYTESSERACT_AVAILABLE and not EASYOCR_AVAILABLE:
                result['text'] = 'OCR not available. Install pytesseract or easyocr for text extraction.'
                result['success'] = True
                return result

            # Choose best result
            if text_results:
                # Use the result with highest confidence, or longest text if no confidence
                best_result = max(text_results, key=lambda x: x['confidence'] or len(x['text']))
                result['text'] = best_result['text']
                result['ocr_results'] = text_results

            result['metadata'] = self._extract_metadata(image)
            result['success'] = True

            self.logger.info(f"Successfully processed image: {file_path.name}")

        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Error processing image {file_path.name}: {e}")

        return result

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')

            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)

            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)

            # Apply noise reduction
            image = image.filter(ImageFilter.MedianFilter())

            return image

        except Exception as e:
            self.logger.warning(f"Image preprocessing failed: {e}")
            return image

    def _extract_with_tesseract(self, image: Image.Image) -> str:
        """Extract text using Tesseract."""
        # Configure Tesseract
        config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=config)
        return text.strip()

    def _get_tesseract_confidence(self, image: Image.Image) -> float:
        """Get average confidence score from Tesseract."""
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            return sum(confidences) / len(confidences) if confidences else 0.0
        except Exception:
            return 0.0

    def _extract_with_easyocr(self, file_path: Path) -> str:
        """Extract text using EasyOCR."""
        if self.easyocr_reader is None:
            self.easyocr_reader = easyocr.Reader(['en'])

        results = self.easyocr_reader.readtext(str(file_path))
        text_parts = [result[1] for result in results]
        return ' '.join(text_parts)

    def _extract_metadata(self, image: Image.Image) -> Dict[str, Any]:
        """Extract image metadata."""
        metadata = {
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height
        }

        # Extract EXIF data if available
        try:
            if hasattr(image, '_getexif'):
                exifdata = image._getexif()
                if exifdata:
                    metadata['exif'] = dict(exifdata)
        except Exception as e:
            self.logger.warning(f"EXIF extraction failed: {e}")

        return metadata