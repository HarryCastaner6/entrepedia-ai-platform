"""
Audio transcription using Whisper and other speech-to-text models.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import wave
from backend.utils.logger import processor_logger

# Optional speech-to-text dependencies
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class AudioProcessor:
    """Extract text from audio files using speech recognition."""

    def __init__(self):
        """Initialize audio processor."""
        self.logger = processor_logger
        self.whisper_model = None

    def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from audio file using transcription.

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary containing transcribed text and metadata
        """
        self.logger.info(f"Processing audio: {file_path.name}")

        result = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_type': 'audio',
            'text': '',
            'transcription': {},
            'metadata': {},
            'success': False,
            'error': None
        }

        try:
            # Extract metadata first
            result['metadata'] = self._extract_metadata(file_path)

            # Transcribe using Whisper if available
            if WHISPER_AVAILABLE:
                transcription = self._transcribe_with_whisper(file_path)

                if transcription:
                    result['text'] = transcription['text']
                    result['transcription'] = transcription
                    result['success'] = True
                    self.logger.info(f"Successfully processed audio: {file_path.name}")
                else:
                    result['error'] = "Transcription failed"
            else:
                result['text'] = 'Audio transcription not available. Install whisper for full functionality.'
                result['success'] = True
                self.logger.info(f"Processed audio metadata (transcription unavailable): {file_path.name}")

        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Error processing audio {file_path.name}: {e}")

        return result

    def _transcribe_with_whisper(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Transcribe audio using OpenAI Whisper."""
        try:
            if self.whisper_model is None:
                self.logger.info("Loading Whisper model...")
                self.whisper_model = whisper.load_model("base")

            self.logger.info(f"Transcribing {file_path.name}...")
            result = self.whisper_model.transcribe(str(file_path))

            return {
                'text': result['text'],
                'language': result.get('language', 'unknown'),
                'segments': result.get('segments', []),
                'engine': 'whisper'
            }

        except Exception as e:
            self.logger.error(f"Whisper transcription failed: {e}")
            return None

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio file metadata."""
        metadata = {
            'file_extension': file_path.suffix.lower(),
            'file_size': file_path.stat().st_size
        }

        # Try to extract basic audio info
        try:
            if file_path.suffix.lower() == '.wav':
                with wave.open(str(file_path), 'rb') as wav_file:
                    metadata.update({
                        'channels': wav_file.getnchannels(),
                        'sample_width': wav_file.getsampwidth(),
                        'framerate': wav_file.getframerate(),
                        'frames': wav_file.getnframes(),
                        'duration': wav_file.getnframes() / wav_file.getframerate()
                    })
        except Exception as e:
            self.logger.warning(f"Audio metadata extraction failed: {e}")

        return metadata