import os
import json
try:
    from execucao.utils import setup_logger, load_env_file
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger, load_env_file

from openai import OpenAI

logger = setup_logger('CopywriterAgent')
load_env_file()

class Copywriter:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_copy(self, product_info, pain_info):
        """
        Generates sales copy for the landing page.
        """
        if not self.client:
            # Fallback for testing without API
            return {
                "headline": "Stop Spending Hours on Monthly Reports",
                "subheadline": "Automate your bank-to-excel workflow in seconds with our simple script.",
                "pain_agitation": "Are you tired of manually copying data from PDF bank statements and making expensive errors?",
                "solution_promise": "Our Python Converter does it for you instantly, with 100% accuracy.",
                "benefits": ["Save 10+ hours per month", "Eliminate copy-paste errors", "No coding skills required"],
                "features": ["Drag & Drop Interface", "Supports all major banks", "Export to CSV/XLSX"],
                "cta_text": "Get Instant Access - $9",
                "pricing_text": "Only $9 (One-time payment)"
            }

        prompt = f"""
        Write high-converting sales copy for a landing page.
        
        Product: {product_info.get('title')}
        Description: {product_info.get('description')}
        Target Pain: {pain_info.get('cluster_name')}
        Pain Score: {pain_info.get('aggregate_pain_score')}
        
        Structure (JSON):
        - headline (Punchy, outcome-focused)
        - subheadline (Clarifies the offer)
        - pain_agitation (Empathize with the problem)
        - solution_promise (How we fix it)
        - benefits (List of 3-5 key benefits)
        - features (List of 3-5 key features)
        - cta_text (Action verb)
        - pricing_text (e.g. "Only $9 for a limited time")
        - faq (List of 3 Q&A pairs)

        Tone: Professional, urgent, persuasive.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a world-class direct response copywriter."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error generating copy: {e}")
            raise  # Re-raise in production instead of falling back to MOCK
