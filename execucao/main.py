import os
import sys
import time
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execucao.utils import setup_logger, load_env_file
from core.event_bus import event_bus
from core.event_schema import build_event

# 1. Structural Components (State, EventBus, Logs)
# 1. Structural Components (State, EventBus, Logs)
logger = setup_logger('MainBootstrap')
load_env_file()

# Global references for checking status
guardian = None
market_loop = None

def bootstrap_system():
    """
    Initializes all engines and controllers.
    """
    global guardian, market_loop
    
    try:
        # 2. Initialize Core Engines
        logger.info(">>> BOOTSTRAPPING AUTONOMOUS SYSTEM <<<")
        
        # Guardian (Supervisor)
        from guardian.guardian_engine import GuardianEngine
        guardian = GuardianEngine()
        logger.info("1. Guardian Engine: ONLINE")

        # 12. Human Checkpoint Engine (Block 12)
        # Must run early to validate infrastructure before Orchestrator
        from core.human_checkpoint import HumanCheckpointRegistry
        human_checkpoint = HumanCheckpointRegistry()
        human_checkpoint.validate_required_credentials()
        logger.info("12. Human Checkpoint: CHECKED")

        # Orchestrator (Central Nervous System)
        # Imported from module where singleton is instantiated
        from core.orchestrator import orchestrator
        logger.info("2. Core Orchestrator: ONLINE")

        # 3. Initialize Domain Controllers (Subscribers)
        # Strategy & Marketing
        from strategy_engine.strategy_controller import strategy_controller
        logger.info("3. Strategy Controller: ONLINE")

        # Pricing & Finance
        from pricing.pricing_engine import PricingEngine
        pricing_engine = PricingEngine() # Manually instantiated as per current design
        logger.info("4. Pricing Engine: ONLINE")

        # Market Loop (Evolution)
        from execucao.market_loop import MarketLoop
        market_loop = MarketLoop()
        logger.info("5. Market Loop: ONLINE")

        # Discovery & Radar (New Controller)
        from radar.discovery_controller import DiscoveryController
        discovery_controller = DiscoveryController()
        logger.info("6. Discovery Controller: ONLINE")

        # Deployment & Web (New Controller)
        from deploy.deployment_controller import DeploymentController
        deployment_controller = DeploymentController()
        logger.info("7. Deployment Controller: ONLINE")

        # 8. Beta Window Engine (Block 2)
        from execucao.beta_manager import BetaManager
        beta_manager = BetaManager()
        logger.info("8. Beta Manager: ONLINE")

        # 11. Telemetry Engine (Block 9)
        from telemetry.telemetry_tracker import TelemetryTracker
        telemetry_tracker = TelemetryTracker()
        logger.info("11. Telemetry Engine: ONLINE")

        # 9. Winner Selection Engine (Block 3)
        from execucao.winner_selection_engine import WinnerSelectionEngine
        winner_engine = WinnerSelectionEngine()
        logger.info("9. Winner Selection Engine: ONLINE")

        # 10. Version Manager (Block 5)
        from execucao.version_manager import VersionManager
        version_manager = VersionManager()
        logger.info("10. Version Manager: ONLINE")

        # 13. Uptime Engine (Block 13)
        from core.uptime_engine import UptimeEngine
        uptime_engine = UptimeEngine()
        logger.info("13. Uptime Engine: ONLINE")

        # 14. Refund Manager (Block 14)
        from pricing.refund_manager import RefundManager
        refund_manager = RefundManager()
        logger.info("14. Refund Manager: ONLINE")

        # 15. Access & Auth Engine (Block 15)
        # Automatically subscribes to purchase_success/refund_completed
        from security.auth_manager import auth_manager
        logger.info("15. Auth Manager: ONLINE")

        # 16. Update & Versioning Engine (Block 16)
        # Instantiated at Block 5/10 slot previously, confirming here for clarity
        # from execucao.version_manager import VersionManager # Already loaded

        # 17. Finance Engine (Block 17)
        from finance_engine.finance_manager import finance_manager
        logger.info("17. Finance Engine: ONLINE")

        # 18. Security Layer (Block 18)
        # Validates critical actions globally
        from security.security_logger import security_logger
        logger.info("18. Security Layer: ONLINE")
        
        # 19. Product Construction Engine (Block 19)
        # Instantiated on demand by Orchestrator/DiscoveryController
        # from product_engine.product_builder import product_builder 

        # 20. Access Control Engine (Block 20)
        # Manages Licenses and Tokens
        from access_control.access_engine import access_engine
        logger.info("20. Access Control Engine: ONLINE")

        # 4. Signal System Start
        logger.info(">>> ALL SYSTEMS GO. EMITTING START SIGNAL... <<<")
        
        startup_event = build_event(
            event_name="system_startup_requested",
            payload={"initiated_by": "main_bootstrap"},
            source="MainBootstrap"
        )
        event_bus.emit("system_startup_requested", startup_event)
        
        return True

    except Exception as e:
        logger.critical(f"CRITICAL BOOTSTRAP FAILURE: {e}")
        # Try one last gasp log
        try:
            if 'guardian' in locals() and guardian:
                guardian.report_incident("MainBootstrap", "critical", str(e))
        except: pass
        sys.exit(1)

def run_system_loop():
    """
    Main execution loop.
    """
    if not guardian:
        logger.error("System loop started without Guardian!")
        return

    logger.info(">>> SYSTEM RUNNING (EVENT-DRIVEN MODE) <<<")
    logger.info("Press Ctrl+C to stop.")
    
    try:
        while True:
            # Run Guardian Surveillance Cycle periodically
            guardian.run_surveillance_cycle()
            
            # Check Pricing/Market Loop periodically if they don't have their own threads
            # (Assuming they act on events or explicit checks)
            # For now, simplistic loop to simulate time passing
            
            # market_loop.check_loop_status(...) could be called here or via scheduled events
            # But per "pure event driven", maybe we rely on events?
            # MarketLoop has `check_loop_status` which needs to be called. 
            # Making Guardian trigger a 'heartbeat' event might be better, 
            # but for now let's keep explicit check or use Orchestrator to emit 'cycle_tick'.
            
            time.sleep(60) # 1 Minute Heartbeat
    except KeyboardInterrupt:
        logger.info(">>> SYSTEM STOPPING <<<")
        sys.exit(0)

if __name__ == "__main__":
    if bootstrap_system():
        run_system_loop()
