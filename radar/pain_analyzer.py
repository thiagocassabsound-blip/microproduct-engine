import os
import json
try:
    from execucao.utils import setup_logger, load_env_file
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger, load_env_file

from openai import OpenAI

logger = setup_logger('PainAnalyzer')
load_env_file()

class PainAnalyzer:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

    def calculate_scores(self, pain_points):
        """
        Calculates scores for a list of pain points.
        """
        if not self.client:
            # Mock scoring
            for p in pain_points:
                p['pain_score'] = 8
                p['urgency_score'] = 7
                p['willingness_to_pay_score'] = 6
                p['frequency_score'] = 5
                p['role_value_score'] = 5
            return pain_points

        # Batch processing for efficiency
        prompt = f"""
        Rate the following pain points on a scale of 1-10 for each criterion:
        - pain_score (Intensity of suffering)
        - urgency_score (How bad they need a fix NOW)
        - frequency_score (How often it happens)
        - role_value_score (Value of the person suffering, e.g. CEO > Intern)
        - willingness_to_pay_score (Likelihood to pay for a solution)

        Input: {json.dumps(pain_points)}

        Return a JSON list of objects, preserving original data and adding the scores.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a product strategist scoring valid market problems."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={ "type": "json_object" }
            )
            data = json.loads(response.choices[0].message.content)
            # Handle list wrapper if present
            if 'scored_pain_points' in data:
                return data['scored_pain_points']
            if isinstance(data, list):
                return data
            for k, v in data.items():
                if isinstance(v, list):
                    return v
            return pain_points

        except Exception as e:
            logger.error(f"Error scoring pain points: {e}")
            raise  # Re-raise in production instead of falling back to MOCK
            return pain_points

    def cluster_pains(self, scored_pains):
        """
        Clusters pain points into potential product opportunities.
        """
        if not self.client:
            # Mock clustering
            return [{
                "cluster_name": "Automated Reporting Tool",
                "aggregate_pain_score": 8.5,
                "contained_pain_ids": [0, 1],
                "potential_solution_hypothesis": "A python script that converts PDF bank statements to Excel."
            }]

        prompt = f"""
        Group the following scored pain points into clusters based on:
        - Tool (e.g. Problems with Excel)
        - Workflow (e.g. Lead Generation issues)
        - Role (e.g. Marketing Manager struggles)
        - Desired Outcome (e.g. Want to save time on reporting)

        For each cluster, provide:
        - cluster_name
        - aggregate_pain_score (average)
        - contained_pain_ids (or indices)
        - potential_solution_hypothesis

        Input: {json.dumps(scored_pains)}
        
        Return JSON object with key 'clusters'.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                response_format={ "type": "json_object" }
            )
            data = json.loads(response.choices[0].message.content)
            return data.get('clusters', [])

        except Exception as e:
            logger.error(f"Error clustering pains: {e}")
            raise  # Re-raise in production instead of falling back to MOCK
