"""
Area Monitoring System - Main Entry Point
Production-grade real-time person detection and zone monitoring
"""

import sys
import argparse
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils import setup_logging, load_config, get_logger
from app.monitor import AreaMonitor

logger = None


def main():
    """Main entry point"""
    global logger
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Area Monitoring System - Real-time person detection and zone monitoring"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory for log files"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    import logging
    log_level = getattr(logging, args.log_level)
    logger = setup_logging(
        log_dir=args.log_dir,
        log_level=log_level,
        console_output=True,
        file_output=True
    )
    
    logger.info("=" * 60)
    logger.info("Area Monitoring System v2.0.0")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        if args.debug:
            config.debug = True
            logger.setLevel(logging.DEBUG)
        
        logger.info(f"Configuration loaded")
        logger.info(f"Camera: {config.camera.name} ({config.camera.width}x{config.camera.height})")
        logger.info(f"Detection threshold: {config.detection.confidence_threshold}")
        logger.info(f"Alert system: {'Enabled' if config.alert.enabled else 'Disabled'}")
        
        # Create and run monitor
        monitor = AreaMonitor(config)
        
        logger.info("Starting monitoring system...")
        monitor.run()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Area Monitoring System stopped")


if __name__ == "__main__":
    main()
