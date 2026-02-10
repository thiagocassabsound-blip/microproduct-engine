import os
import sys
import json
import time
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execucao.utils import setup_logger, load_env_file
from guardian.monitor import Guardian
from radar.search_engine import SearchAgent
from radar.fetcher import FetchAgent
from radar.parser import ParserAgent
from radar.pain_analyzer import PainAnalyzer
from radar.competitor_scan import CompetitorScan
from produtos.generator import ProductGenerator
from paginas.copywriter import Copywriter
from paginas.builder import PageBuilder
from deploy.manager import DeployManager
from deploy.validator import validate_url
from telemetria.tracker import TelemetryTracker
from pricing.stripe_manager import StripeManager

logger = setup_logger('MainOrchestrator')
load_env_file()
guardian = Guardian()

def load_directives():
    # Load search queries
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'diretivas/radar/search_queries.json'), 'r') as f:
            return json.load(f)
    except:
        return {"queries": ["productivity tools pain points"]}

def pipeline():
    logger.info(">>> STARTING AUTONOMOUS CYCLE <<<")
    
    # 1. DISCOVERY
    logger.info("--- PHASE 1: DISCOVERY ---")
    directives = load_directives()
    query = random.choice(directives['queries'])
    
    search_agent = SearchAgent()
    results = search_agent.run(query)
    
    if not results:
        logger.warning("No search results found. Aborting cycle.")
        return

    fetch_agent = FetchAgent()
    parser_agent = ParserAgent()
    pain_analyzer = PainAnalyzer()
    
    all_pains = []
    
    # Process top 3 results to save time/tokens
    for result in results[:3]:
        logger.info(f"Processing: {result['title']}")
        html = fetch_agent.run(result['link'])
        if not html: continue
        
        pains = parser_agent.run(html, result['link'])
        if pains:
            logger.info(f"Found {len(pains)} pain points.")
            all_pains.extend(pains)
            
    if not all_pains:
        logger.warning("No pain points extracted. Aborting cycle.")
        return

    # Score and Cluster
    scored_pains = pain_analyzer.calculate_scores(all_pains)
    clusters = pain_analyzer.cluster_pains(scored_pains)
    
    if not clusters:
        logger.warning("No clusters formed.")
        return
        
    # Select best cluster (simple logic: highest pain score)
    best_cluster = max(clusters, key=lambda c: c.get('aggregate_pain_score', 0))
    logger.info(f"Selected Champion Cluster: {best_cluster.get('cluster_name')} (Score: {best_cluster.get('aggregate_pain_score')})")

    # 2. ANALYSIS
    logger.info("--- PHASE 2: ANALYSIS ---")
    competitor_scan = CompetitorScan()
    # Mocking competitor data for now, in real generic search we'd search specifically for competitors
    gap_analysis = competitor_scan.analyze_gaps(best_cluster, "General market data suggests generic tools.")
    logger.info("Gap Analysis complete.")

    # 3. PRODUCT GENERATION (Loop for 3 variations)
    logger.info("--- PHASE 3: PRODUCT GENERATION & DEPLOYMENT LOOP ---")
    product_gen = ProductGenerator()
    
    # Try 3 different angles/types
    product_types = ["checklist", "script", "spreadsheet"]
    
    for p_type in product_types:
        logger.info(f">> Generating Product Variation: {p_type.upper()}")
        
        product_path = product_gen.run(best_cluster, gap_analysis, p_type)
        if not product_path:
            logger.error(f"Failed to generate {p_type}. Skipping.")
            continue
            
        product_info = {
            "title": f"{best_cluster.get('cluster_name')} {p_type.title()}",
            "description": best_cluster.get('potential_solution_hypothesis'),
            "path": product_path
        }

        # 4. WEB & DEPLOY
        copywriter = Copywriter()
        page_builder = PageBuilder()
        deploy_manager = DeployManager()
        stripe_manager = StripeManager()
        
        copy_data = copywriter.generate_copy(product_info, best_cluster)
        if not copy_data:
            logger.error("Failed to generate copy. Skipping.")
            continue

        # Use generated headline as product name if available
        product_name = copy_data.get('headline', product_info['title'])

        # 4.1 PAYMENT LINK GENERATION
        # Extract price from copy or use default
        price = 9.00 # Default
        checkout_url = stripe_manager.create_payment_link(product_name, price, product_info['description'])
        
        # Build HTML
        html_filename = f"landing_page_{p_type}.html"
        html_output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp', html_filename)
        built_page = page_builder.build_page(copy_data, product_name, html_output_path, checkout_url)
        
        if built_page:
            # 5. DEPLOYMENT (Vercel)
            import re
            safe_slug = re.sub(r'[^a-z0-9-]', '', product_name.lower().replace(' ', '-'))[:40]
            # Make unique slug per type
            product_slug = f"{safe_slug}-{p_type}"
            
            # Deploy locally first for safety/backup
            local_url = deploy_manager.run(built_page, product_slug, mode='local')
            
            # Try Vercel deployment
            live_url = deploy_manager.run(built_page, product_slug, mode='vercel')
            
            if not live_url:
                live_url = local_url
                
            logger.info(f"🚀 DEPLOY SUCCESSFUL ({p_type}): {live_url}")
            
            # 5.1 BROWSER VALIDATION
            is_valid = validate_url(live_url)
            if is_valid:
                logger.info("✅ Browser Validation Passed")
            else:
                logger.error("❌ Browser Validation Failed (Check logs)")

            # 5. LOGGING/TELEMETRY
            tracker = TelemetryTracker()
            tracker.track_event('deploy', {"url": live_url, "cluster": best_cluster.get('cluster_name'), "type": p_type, "validated": is_valid})
        
    logger.info(">>> CYCLE COMPLETE <<<")

if __name__ == "__main__":
    # Use Guardian to run the pipeline
    guardian.watch(pipeline)
