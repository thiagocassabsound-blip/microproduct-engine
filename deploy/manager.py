import os
import shutil
try:
    from execucao.utils import setup_logger, load_env_file
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger, load_env_file

logger = setup_logger('DeployManager')
load_env_file()

class DeployManager:
    def __init__(self):
        self.deploy_token = os.getenv("DEPLOY_TOKEN")
        self.domain = os.getenv("VERCEL_DOMAIN")
        if not self.domain:
            # Fallback to legacy for transition, then raise if both missing
            self.domain = os.getenv("DOMAIN_NAME", "localhost")
            if self.domain == "localhost":
                 logger.warning("VERCEL_DOMAIN not set. Using localhost.")

    def deploy_local(self, html_path, product_slug):
        """
        Deploys to a local 'public' directory for serving.
        """
        public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
        os.makedirs(public_dir, exist_ok=True)
        
        target_dir = os.path.join(public_dir, product_slug)
        os.makedirs(target_dir, exist_ok=True)
        
        target_file = os.path.join(target_dir, 'index.html')
        
        try:
            shutil.copy2(html_path, target_file)
            logger.info(f"Deployed locally to: {target_file}")
            return f"http://{self.domain}/{product_slug}" # Mock URL
        except Exception as e:
            logger.error(f"Error checking local deploy: {e}")
            return None

    def _get_files_for_deployment(self, directory):
        """
        Helper to read all files in a directory for Vercel deployment.
        """
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    data = f.read()
                
                # Vercel needs relative paths
                rel_path = os.path.relpath(file_path, directory).replace("\\", "/")
                files.append({
                    "file": rel_path,
                    "data": data
                })
        return files

    def deploy_vercel(self, html_path, product_slug):
        """
        Deploys to Vercel using the API.
        """
        token = os.getenv("VERCEL_API_TOKEN") or self.deploy_token
        
        if not token:
            logger.warning("No VERCEL_API_TOKEN found. Skipping remote deploy.")
            return None
            
        public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
        target_dir = os.path.join(public_dir, product_slug)
        
        # Ensure the file is in the target dir (it should be allowed by deploy_local, but just in case)
        if not os.path.exists(os.path.join(target_dir, 'index.html')):
             # If deploy_local wasn't run or failed, copy it now
             self.deploy_local(html_path, product_slug)

        logger.info(f"Deploying {product_slug} to Vercel...")
        
        files = self._get_files_for_deployment(target_dir)
        
        url = "https://api.vercel.com/v13/deployments"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": product_slug,
            "files": files,
            "projectSettings": {
                "framework": None
            }
        }
        
        try:
            import requests # Make sure we have requests
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                deployment_data = response.json()
                deploy_url = deployment_data.get('url') # vercel.app url
                logger.info(f"Vercel Deployment Successful: https://{deploy_url}")
                return f"https://{deploy_url}"
            else:
                logger.error(f"Vercel Deployment failed: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error deploying to Vercel: {e}")
            return None

    def run(self, html_path, product_slug, mode='vercel'):
        if mode == 'local':
            return self.deploy_local(html_path, product_slug)
        else:
            # Default to Vercel if not local
            return self.deploy_vercel(html_path, product_slug)
