import os
import json
try:
    from execucao.utils import setup_logger, load_env_file
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger, load_env_file

from openai import OpenAI

logger = setup_logger('CompetitorScan')
load_env_file()

class CompetitorScan:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def analyze_gaps(self, cluster_info, competitor_data_text):
        """
        Identifies gaps in existing solutions based on user complaints.
        """
        if not self.client:
            return {
                "ignored_complaints": ["Complex UI", "No PDF support"],
                "price_gaps": ["Competitors charge >$50/mo"],
                "usability_gaps": ["Requires coding knowledge"]
            }

        prompt = f"""
        Analyze the competitor landscape described below against the pain cluster "{cluster_info.get('cluster_name')}".
         Identify GAPS where competitors are failing. Look for:
        - Complaints about complexity
        - Missing features
        - High price
        - Poor support
        - Slow results

        Competitor Data:
        {competitor_data_text}

        Return a JSON object 'gap_map' with keys: 'ignored_complaints', 'price_gaps', 'usability_gaps'.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in gap analysis: {e}")
            logger.warning("Falling back to MOCK gap analysis due to error.")
            return {
                "ignored_complaints": ["Complex UI", "No PDF support"],
                "price_gaps": ["Competitors charge >$50/mo"],
                "usability_gaps": ["Requires coding knowledge"]
            }

    def calculate_differentiation(self, my_solution_proposal, competitor_info):
        """
        Calculates a differentiation score.
        """
        # Real differentiation logic
        if not self.client:
             return {"differentiation_score": 8.5, "analysis": "Mock analysis: Predicted higher speed to value."}

        prompt = f"""
        Compare my proposed solution against the competitor landscape.
        
        My Solution: {my_solution_proposal}
        Competitor Info: {competitor_info}
        
        Calculate a 'differentiation_score' (1-10) based on:
        - Uniqueness of mechanism
        - Speed to result
        - Price advantage
        
        Provide a short 'analysis' explaining the score.
        
        Return JSON with keys: 'differentiation_score', 'analysis'.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error calculating differentiation: {e}")
            logger.warning("Falling back to MOCK differentiation.")
            return {"differentiation_score": 8.5, "analysis": "Mock analysis: Predicted higher speed to value."}
