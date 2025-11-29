"""
Robust web scraper for Entrepedia platform.
Handles authentication, file discovery, and downloading with retry logic.
"""
import os
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from backend.utils.config import settings
from backend.utils.logger import scraper_logger
from backend.scraper.auth_handler import EntrepediaAuth
from backend.scraper.file_downloader import FileDownloader


class EntrepediaScraper:
    """
    Main scraper class for Entrepedia platform.
    Discovers and downloads all course materials.
    """

    # Supported file extensions
    SUPPORTED_EXTENSIONS = [
        '.pdf', '.docx', '.doc', '.pptx', '.ppt',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp',
        '.mp3', '.wav', '.m4a',
        '.mp4', '.avi', '.mov', '.mkv',
        '.txt', '.csv', '.xlsx', '.xls'
    ]

    def __init__(self):
        """Initialize scraper with configuration."""
        self.base_url = settings.entrepedia_base_url
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.auth = EntrepediaAuth()
        self.downloader = FileDownloader()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        scraper_logger.info("EntrepediaScraper initialized")

    def login(self) -> bool:
        """
        Authenticate with Entrepedia platform.

        Returns:
            True if login successful, False otherwise
        """
        try:
            success = self.auth.login(self.session)
            if success:
                scraper_logger.info("Successfully logged into Entrepedia")
            else:
                scraper_logger.error("Failed to log into Entrepedia")
            return success
        except Exception as e:
            scraper_logger.error(f"Login error: {e}")
            return False

    def discover_courses(self) -> List[Dict[str, Any]]:
        """
        Discover all available courses on the platform.

        Returns:
            List of course metadata dictionaries
        """
        courses = []

        try:
            # Navigate to courses page
            courses_url = urljoin(self.base_url, "/courses")
            response = self.session.get(courses_url, timeout=settings.request_timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find course links (adjust selectors based on actual Entrepedia structure)
            course_elements = soup.find_all('a', class_=['course-link', 'course-card'])

            for element in course_elements:
                course_url = urljoin(self.base_url, element.get('href', ''))
                course_title = element.get_text(strip=True)

                courses.append({
                    'title': course_title,
                    'url': course_url,
                    'id': self._extract_course_id(course_url)
                })

            scraper_logger.info(f"Discovered {len(courses)} courses")

        except Exception as e:
            scraper_logger.error(f"Error discovering courses: {e}")

        return courses

    def discover_course_files(self, course_url: str) -> List[Dict[str, Any]]:
        """
        Discover all downloadable files within a course.

        Args:
            course_url: URL of the course page

        Returns:
            List of file metadata dictionaries
        """
        files = []

        try:
            response = self.session.get(course_url, timeout=settings.request_timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(self.base_url, href)

                # Check if it's a downloadable file
                if self._is_supported_file(full_url):
                    file_name = self._extract_filename(full_url, link.get_text(strip=True))

                    files.append({
                        'url': full_url,
                        'filename': file_name,
                        'type': self._get_file_type(file_name),
                        'source_page': course_url
                    })

            # Also check for embedded documents, iframes, etc.
            files.extend(self._find_embedded_files(soup, course_url))

            scraper_logger.info(f"Found {len(files)} files in course")

        except Exception as e:
            scraper_logger.error(f"Error discovering course files: {e}")

        return files

    def scrape_all(self) -> List[Dict[str, Any]]:
        """
        Complete scraping workflow: login, discover courses, download all files.

        Returns:
            List of all downloaded file metadata
        """
        scraper_logger.info("Starting complete scraping workflow")

        # Step 1: Login
        if not self.login():
            scraper_logger.error("Cannot proceed without authentication")
            return []

        # Step 2: Discover courses
        courses = self.discover_courses()

        if not courses:
            scraper_logger.warning("No courses found")
            return []

        # Step 3: Download all files from all courses
        all_files = []

        for course in tqdm(courses, desc="Processing courses"):
            scraper_logger.info(f"Processing course: {course['title']}")

            # Create course directory
            course_dir = self.output_dir / self._sanitize_filename(course['title'])
            course_dir.mkdir(parents=True, exist_ok=True)

            # Discover files
            files = self.discover_course_files(course['url'])

            # Download files
            for file_info in tqdm(files, desc=f"Downloading {course['title']}", leave=False):
                try:
                    downloaded_path = self.downloader.download(
                        file_info['url'],
                        course_dir,
                        file_info['filename'],
                        self.session
                    )

                    if downloaded_path:
                        file_info['local_path'] = str(downloaded_path)
                        file_info['course'] = course['title']
                        file_info['course_id'] = course['id']
                        all_files.append(file_info)

                except Exception as e:
                    scraper_logger.error(f"Failed to download {file_info['filename']}: {e}")

            # Be respectful - add delay between courses
            time.sleep(2)

        scraper_logger.info(f"Scraping complete. Downloaded {len(all_files)} files")
        return all_files

    def _is_supported_file(self, url: str) -> bool:
        """Check if URL points to a supported file type."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        return any(path.endswith(ext) for ext in self.SUPPORTED_EXTENSIONS)

    def _get_file_type(self, filename: str) -> str:
        """Determine file category from extension."""
        ext = Path(filename).suffix.lower()

        if ext in ['.pdf']:
            return 'pdf'
        elif ext in ['.docx', '.doc']:
            return 'docx'
        elif ext in ['.pptx', '.ppt']:
            return 'pptx'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return 'image'
        elif ext in ['.mp3', '.wav', '.m4a']:
            return 'audio'
        elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
            return 'video'
        else:
            return 'other'

    def _extract_filename(self, url: str, link_text: str) -> str:
        """Extract or generate filename from URL and link text."""
        parsed = urlparse(url)
        path = parsed.path

        # Try to get filename from URL
        filename = os.path.basename(path)

        # If no filename in URL, use link text
        if not filename or '.' not in filename:
            filename = self._sanitize_filename(link_text) + '.pdf'  # Default to PDF

        return filename

    def _extract_course_id(self, url: str) -> str:
        """Extract course ID from URL."""
        # Extract ID from URL pattern (adjust based on actual Entrepedia URLs)
        parts = url.rstrip('/').split('/')
        return parts[-1] if parts else 'unknown'

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Limit length
        return filename[:200]

    def _find_embedded_files(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Find files embedded in iframes, embeds, etc."""
        embedded = []

        # Check iframes
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if src and self._is_supported_file(src):
                full_url = urljoin(page_url, src)
                embedded.append({
                    'url': full_url,
                    'filename': self._extract_filename(full_url, 'embedded_file'),
                    'type': self._get_file_type(full_url),
                    'source_page': page_url
                })

        # Check embed tags
        for embed in soup.find_all('embed'):
            src = embed.get('src', '')
            if src and self._is_supported_file(src):
                full_url = urljoin(page_url, src)
                embedded.append({
                    'url': full_url,
                    'filename': self._extract_filename(full_url, 'embedded_file'),
                    'type': self._get_file_type(full_url),
                    'source_page': page_url
                })

        return embedded