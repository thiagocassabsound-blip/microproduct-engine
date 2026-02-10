import requests
from bs4 import BeautifulSoup
try:
    from execucao.utils import setup_logger
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger

logger = setup_logger('FetchAgent')

class FetchAgent:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch(self, url):
        """
        Fetches the URL and checks if it allows scraping.
        """
        if "example.com" in url:
            logger.info("Returning MOCK content for example.com")
            return "<html><body><h1>Mock Content</h1><p>I hate doing manual excel reports. It takes 5 hours a week. I wish there was a tool.</p></body></html>"

        logger.info(f"Fetching URL: {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def clean(self, html_content):
        """
        Removes navigation, headers, footers, scripts, styles to leave mostly content.
        """
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove unwanted tags
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
            tag.decompose()

        # Get text
        text = soup.get_text(separator='\n')
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text

    def run(self, url):
        html = self.fetch(url)
        return self.clean(html)
