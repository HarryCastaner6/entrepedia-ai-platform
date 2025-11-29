"""
Robust file downloader with retry logic and progress tracking.
"""
import os
import time
from pathlib import Path
from typing import Optional
import requests
from tqdm import tqdm
from backend.utils.config import settings
from backend.utils.logger import scraper_logger


class FileDownloader:
    """Handle file downloads with retry logic and progress tracking."""

    def __init__(self, max_retries: int = 3, chunk_size: int = 8192):
        """
        Initialize file downloader.

        Args:
            max_retries: Maximum number of download retry attempts
            chunk_size: Size of chunks for streaming downloads
        """
        self.max_retries = max_retries
        self.chunk_size = chunk_size

    def download(
        self,
        url: str,
        output_dir: Path,
        filename: str,
        session: requests.Session
    ) -> Optional[Path]:
        """
        Download a file with retry logic.

        Args:
            url: URL to download from
            output_dir: Directory to save file
            filename: Name for the downloaded file
            session: Requests session to use

        Returns:
            Path to downloaded file, or None if failed
        """
        output_path = output_dir / filename

        # Skip if already exists
        if output_path.exists():
            scraper_logger.info(f"File already exists: {filename}")
            return output_path

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                scraper_logger.info(f"Downloading {filename} (attempt {attempt + 1}/{self.max_retries})")

                response = session.get(
                    url,
                    stream=True,
                    timeout=settings.request_timeout
                )
                response.raise_for_status()

                # Get file size if available
                total_size = int(response.headers.get('content-length', 0))

                # Download with progress bar
                with open(output_path, 'wb') as f:
                    if total_size:
                        with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                            for chunk in response.iter_content(chunk_size=self.chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                    else:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if chunk:
                                f.write(chunk)

                scraper_logger.info(f"Successfully downloaded: {filename}")
                return output_path

            except Exception as e:
                scraper_logger.error(f"Download attempt {attempt + 1} failed: {e}")

                # Clean up partial download
                if output_path.exists():
                    output_path.unlink()

                # Wait before retry
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    scraper_logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)

        scraper_logger.error(f"Failed to download {filename} after {self.max_retries} attempts")
        return None