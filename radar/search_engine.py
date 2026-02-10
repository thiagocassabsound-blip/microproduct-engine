import requests
from bs4 import BeautifulSoup
import time
import random
try:
    from execucao.utils import setup_logger
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger

logger = setup_logger('SearchEngine')

class SearchAgent:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def search_google(self, query, max_results=10):
        """
        Performs a search on Google using requests and BeautifulSoup.
        Note: This is brittle and may be blocked.
        """
        url = "https://www.google.com/search"
        params = {'q': query, 'num': max_results}
        results = []
        
        logger.info(f"Searching Google for: {query}")
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for result in soup.select('.tF2Cxc'): # Common Google result class
                if len(results) >= max_results:
                    break
                    
                title_elem = result.select_one('h3')
                link_elem = result.select_one('a')
                snippet_elem = result.select_one('.VwiC3b')
                
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(),
                        'link': link_elem['href'],
                        'snippet': snippet_elem.get_text() if snippet_elem else "",
                        'source': 'google'
                    })
            
            if results:
                 logger.info(f"Found {len(results)} results on Google")
                 return results
                 
            # Fallback for different DOM structure
            for result in soup.select('div.g'):
                if len(results) >= max_results:
                    break
                title_elem = result.select_one('h3')
                link_elem = result.select_one('a')
                if title_elem and link_elem:
                     results.append({
                        'title': title_elem.get_text(),
                        'link': link_elem['href'],
                        'snippet': "",
                        'source': 'google'
                    })

            logger.info(f"Found {len(results)} results on Google")
            return results

        except Exception as e:
            logger.error(f"Error searching Google: {e}")
            return []

    def search_duckduckgo(self, query, max_results=10):
        """
        Performs a search on DuckDuckGo using the HTML version to avoid JS requirements.
        """
        url = "https://html.duckduckgo.com/html/"
        data = {'q': query}
        results = []

        logger.info(f"Searching DuckDuckGo for: {query}")
        
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for i, result in enumerate(soup.find_all('div', class_='result')):
                if i >= max_results:
                    break
                
                title_tag = result.find('a', class_='result__a')
                if not title_tag:
                    continue
                    
                link = title_tag['href']
                title = title_tag.get_text(strip=True)
                snippet_tag = result.find('a', class_='result__snippet')
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'source': 'duckduckgo'
                })
                
            logger.info(f"Found {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}")
            return []


    def run(self, query):
        # Add random delay to be polite
        time.sleep(random.uniform(1, 3))
        
        # Try Google First
        results = self.search_google(query)
        if results:
            return results
            
        # Fallback to DuckDuckGo
        logger.warning("Google search failed or empty. Falling back to DuckDuckGo.")
        results = self.search_duckduckgo(query)
        
        if not results:
            logger.warning("Search failed or returned 0 results. Returning MOCK results.")
            return [
                {
                    "title": "MOCK: How to automate excel reporting",
                    "link": "https://example.com/excel-automation",
                    "snippet": "Learn how to use Python to automate monthly excel reports.",
                    "source": "duckduckgo"
                },
                {
                    "title": "MOCK: Manual data entry pain",
                    "link": "https://example.com/data-entry-pain",
                    "snippet": "Data entry is the worst part of my job.",
                    "source": "duckduckgo"
                }
            ]
        return results

if __name__ == "__main__":
    agent = SearchAgent()
    results = agent.run("how to automate content creation")
    for r in results:
        print(f"{r['title']} - {r['link']}")
