"""
Authentication handler for Entrepedia platform.
Supports form-based login and session management.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from backend.utils.config import settings
from backend.utils.logger import scraper_logger


class EntrepediaAuth:
    """Handle authentication with Entrepedia platform."""

    def __init__(self):
        """Initialize authentication handler."""
        self.base_url = settings.entrepedia_base_url
        self.username = settings.entrepedia_username
        self.password = settings.entrepedia_password

    def login(self, session: requests.Session) -> bool:
        """
        Perform login to Entrepedia platform.

        Args:
            session: Requests session to use for login

        Returns:
            True if login successful, False otherwise
        """
        try:
            # Step 1: Get login page to extract CSRF token if needed
            login_url = urljoin(self.base_url, "/login")

            response = session.get(login_url, timeout=settings.request_timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract CSRF token if present
            csrf_token = self._extract_csrf_token(soup)

            # Step 2: Prepare login data
            login_data = {
                'username': self.username,
                'email': self.username,  # Some platforms use email
                'password': self.password
            }

            if csrf_token:
                login_data['csrf_token'] = csrf_token
                login_data['_csrf'] = csrf_token

            # Step 3: Submit login form
            response = session.post(
                login_url,
                data=login_data,
                timeout=settings.request_timeout,
                allow_redirects=True
            )

            # Step 4: Verify login success
            if self._is_logged_in(response, session):
                scraper_logger.info("Login successful")
                return True
            else:
                scraper_logger.error("Login failed - invalid credentials or form structure")
                return False

        except Exception as e:
            scraper_logger.error(f"Login exception: {e}")
            return False

    def _extract_csrf_token(self, soup: BeautifulSoup) -> str | None:
        """Extract CSRF token from login form."""
        # Try common CSRF token field names
        csrf_fields = ['csrf_token', '_csrf', 'csrfmiddlewaretoken', 'authenticity_token']

        for field_name in csrf_fields:
            token_input = soup.find('input', {'name': field_name})
            if token_input and token_input.get('value'):
                return token_input['value']

        # Check meta tags
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta and csrf_meta.get('content'):
            return csrf_meta['content']

        return None

    def _is_logged_in(self, response: requests.Response, session: requests.Session) -> bool:
        """
        Check if login was successful.

        Args:
            response: Response from login POST request
            session: Session object

        Returns:
            True if logged in, False otherwise
        """
        # Method 1: Check for redirect to dashboard
        if 'dashboard' in response.url or 'courses' in response.url:
            return True

        # Method 2: Check for login error messages
        soup = BeautifulSoup(response.text, 'html.parser')
        error_indicators = ['invalid', 'incorrect', 'failed', 'error']

        page_text = soup.get_text().lower()
        if any(indicator in page_text for indicator in error_indicators):
            return False

        # Method 3: Check for user-specific elements
        user_elements = soup.find_all(['a', 'div'], class_=['user-menu', 'profile', 'logout'])
        if user_elements:
            return True

        # Method 4: Try accessing a protected page
        try:
            test_response = session.get(
                urljoin(self.base_url, "/courses"),
                timeout=settings.request_timeout
            )

            # If we're redirected to login, we're not logged in
            if 'login' in test_response.url:
                return False

            return test_response.status_code == 200

        except Exception:
            return False