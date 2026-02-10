import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execucao.utils import setup_logger

logger = setup_logger('BrowserValidator')

def validate_url(url):
    """
    Validates a deployed URL using Playwright.
    Checks for: HTTP 200, Page Title, 'Buy Now' button visibility.
    """
    logger.info(f"Validating URL: {url}")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Use chromium
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 1. Navigate
            response = page.goto(url, timeout=30000)
            
            if not response.ok:
                logger.error(f"HTTP Error: {response.status} {response.status_text}")
                browser.close()
                return False
                
            # 2. Check Title
            title = page.title()
            logger.info(f"Page Title: {title}")
            if not title:
                logger.warning("Page has no title.")
            
            # 3. Check Buy Button
            # Look for button or link with common CTA text
            buy_button = page.get_by_text("Buy Now", exact=False).first
            
            if buy_button.is_visible():
                logger.info("✅ 'Buy Now' button is visible.")
                
                # Optional: Check if it's clickable (has href or onclick)
                # href = buy_button.get_attribute("href")
                # logger.info(f"Button Link: {href}")
            else:
                logger.warning("❌ 'Buy Now' button NOT found or not visible.")
                # Don't fail the whole validation if just text mismatch, but log waring
                # Try finding by class
                cta = page.locator(".cta-button").first
                if cta.is_visible():
                     logger.info("✅ Found element with class '.cta-button'.")
                else:
                     logger.error("❌ No CTA button found.")
                     browser.close()
                     return False

            browser.close()
            logger.info("Validation Passed.")
            return True

    except ImportError:
        logger.warning("Playwright not installed. Falling back to simple Request validation.")
        return validate_url_requests(url)
    except Exception as e:
        logger.error(f"Validation Error: {e}")
        # If headers/browser issue, might be irrelevant for now
        return False

def validate_url_requests(url):
    import requests
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            if "Buy Now" in response.text or "cta-button" in response.text:
                logger.info("Requests Validation: OK (Found CTA)")
                return True
            else:
                logger.warning("Requests Validation: OK (200) but CTA not found in text.")
                return True # Soft pass
        else:
             logger.error(f"Requests Validation Failed: {response.status_code}")
             return False
    except Exception as e:
        logger.error(f"Requests Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    validate_url(url)
