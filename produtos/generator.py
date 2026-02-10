import os
import json
try:
    from execucao.utils import setup_logger, load_env_file
    from produtos.templates import CHECKLIST_TEMPLATE, SCRIPT_TEMPLATE
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger, load_env_file
    from produtos.templates import CHECKLIST_TEMPLATE, SCRIPT_TEMPLATE

from openai import OpenAI
import pandas as pd

logger = setup_logger('MakerAgent')
load_env_file()

class ProductGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_product_content(self, cluster_info, gap_analysis, product_type="checklist"):
        """
        Generates the content for the product using LLM.
        """
        if not self.client:
            if product_type == 'checklist':
                return {
                    "title": "Monthly Reporting Checklist",
                    "description": "A simple checklist to streamline your end-of-month reporting.",
                    "items": ["Export data from Bank", "Convert PDF to CSV", "Import to Excel Template", "Verify totals"],
                    "next_steps": "Automate this with our script."
                }
            elif product_type == 'script':
                 return {
                    "title": "PDF to Excel Converter",
                    "description": "Python script to convert bank statements to excel.",
                    "code_logic": "print('Converting PDF...')"
                }
            return None

        prompt = f"""
        Create the content for a microproduct based on:
        - Pain Cluster: {cluster_info.get('cluster_name')}
        - Solution Hypothesis: {cluster_info.get('potential_solution_hypothesis')}
        - Gap Analysis: {gap_analysis}
        
        Product Type: {product_type}

        If Checklist: Return JSON with 'title', 'description', 'items' (list of strings), 'next_steps'.
        If Script: Return JSON with 'title', 'description', 'code_logic' (python code snippet).
        If Spreadsheet: Return JSON with 'title', 'description', 'columns' (list), 'rows' (list of lists/dicts).

        Ensure the content provides IMMEDIATE value and solves the specific pain point.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert product builder."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error generating product content: {e}")
            logger.warning("Falling back to MOCK product content due to error.")
            if product_type == 'checklist':
                return {
                    "title": "Monthly Reporting Checklist",
                    "description": "A simple checklist to streamline your end-of-month reporting.",
                    "items": ["Export data from Bank", "Convert PDF to CSV", "Import to Excel Template", "Verify totals"],
                    "next_steps": "Automate this with our script."
                }
            elif product_type == 'script':
                 return {
                    "title": "PDF to Excel Converter",
                    "description": "Python script to convert bank statements to excel.",
                    "code_logic": "print('Converting PDF...')"
                }
            return None

    def create_file(self, content_data, product_type, output_dir):
        """
        Writes the product to a file.
        """
        if not content_data:
            return None

        os.makedirs(output_dir, exist_ok=True)
        filename = f"{content_data.get('title', 'product').lower().replace(' ', '_')}"
        
        if product_type == 'checklist':
            full_path = os.path.join(output_dir, f"{filename}.md")
            items_str = "\n".join([f"- [ ] {item}" for item in content_data.get('items', [])])
            filled_template = CHECKLIST_TEMPLATE.format(
                title=content_data.get('title'),
                description=content_data.get('description'),
                items=items_str,
                next_steps=content_data.get('next_steps', '')
            )
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(filled_template)
            return full_path

        elif product_type == 'script':
            full_path = os.path.join(output_dir, f"{filename}.py")
            filled_template = SCRIPT_TEMPLATE.format(
                title=content_data.get('title'),
                description=content_data.get('description'),
                code_logic=content_data.get('code_logic', '# No logic generated')
            )
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(filled_template)
            return full_path

        elif product_type == 'spreadsheet':
            full_path = os.path.join(output_dir, f"{filename}.csv")
            try:
                df = pd.DataFrame(content_data.get('rows', []), columns=content_data.get('columns', []))
                df.to_csv(full_path, index=False)
                return full_path
            except Exception as e:
                logger.error(f"Error creating CSV: {e}")
                return None

        return None

    def run(self, cluster_info, gap_analysis, product_type="checklist"):
        # Default to temp directory for generation
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp', 'generated_products')
        
        content = self.generate_product_content(cluster_info, gap_analysis, product_type)
        if content:
            filepath = self.create_file(content, product_type, output_dir)
            logger.info(f"Product generated at: {filepath}")
            return filepath
        return None
