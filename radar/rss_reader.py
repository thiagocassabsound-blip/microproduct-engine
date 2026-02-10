import feedparser
import time
try:
    from execucao.utils import setup_logger
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger

logger = setup_logger('RSSReader')

class RSSReader:
    def __init__(self, feeds=None):
        self.feeds = feeds or []
        # Example feeds if none provided
        if not self.feeds:
            self.feeds = [
                "https://www.reddit.com/r/marketing/new/.rss",
                "https://www.reddit.com/r/smallbusiness/new/.rss",
                # Add more relevant feeds here
            ]

    def fetch_feeds(self):
        all_entries = []
        for feed_url in self.feeds:
            logger.info(f"Checking feed: {feed_url}")
            try:
                feed = feedparser.parse(feed_url)
                if feed.bozo:
                    logger.warning(f"Error parsing feed {feed_url}: {feed.bozo_exception}")
                    continue
                
                logger.info(f"Found {len(feed.entries)} entries in {feed_url}")
                
                for entry in feed.entries:
                    all_entries.append({
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': feed_url
                    })
            except Exception as e:
                logger.error(f"Error checking feed {feed_url}: {e}")
        
        return all_entries

    def run(self):
        return self.fetch_feeds()

if __name__ == "__main__":
    reader = RSSReader()
    entries = reader.run()
    print(f"Total entries found: {len(entries)}")
    if entries:
        print(f"Sample: {entries[0]}")
