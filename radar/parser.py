import os
import json
try:
    from execucao.utils import setup_logger, load_env_file
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger, load_env_file

from bs4 import BeautifulSoup
from openai import OpenAI

logger = setup_logger('ParserAgent')
load_env_file()

class ParserAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not configured. Pain point parsing requires this environment variable.")
            raise ValueError("Pain point parsing requires OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=api_key)
        logger.info("✅ OpenAI client initialized for Parser")

    def extract_pain_points(self, text_content, source_url=""):
        """
        Extracts structured pain points from text using LLM.
        """
        # Client validation happens in __init__, so this should never be None in production

        if len(text_content) > 10000:
             # Try to clean it better first if it's raw HTML disguised as text
             try:
                 soup = BeautifulSoup(text_content, 'html.parser')
                 # Remove noise
                 for noise in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'ads']):
                     noise.decompose()
                 text_content = soup.get_text(separator=' ', strip=True)
             except:
                 pass # If it fails, use as is

             text_content = text_content[:10000] # Truncate for token limits

        prompt = f"""
        Analyze the following text from {source_url} and extract user pain points, frustrations, and problems.
        Focus on:
        - Description of the problem
        - Frustration level (High/Medium/Low)
        - Time wasted
        - Tool failures
        - Limitations
        - Cost issues
        - Complexity

        Return the result as a JSON list of objects with keys: 'problem', 'frustration_level', 'context'.
        If no pain points are found, return an empty list [].

        Text content:
        {text_content}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Or gpt-4
                messages=[
                    {"role": "system", "content": "You are a market research analyst extracting user pain points."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Handle potential different json structures (e.g. wrapper keys)
            if 'pain_points' in data:
                return data['pain_points']
            if isinstance(data, list):
                return data
            
            # If it's a dict but not 'pain_points', try to find a list value
            for key, value in data.items():
                if isinstance(value, list):
                    return value
            
            return []

        except Exception as e:
            logger.error(f"Error parsing with LLM: {e}")
            raise  # Re-raise in production instead of falling back to MOCK

    def run(self, text, url=""):
        return self.extract_pain_points(text, url)
