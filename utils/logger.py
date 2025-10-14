"""
Logging configuration for penetration testing agent
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logging(session_id: str, log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """Set up comprehensive logging for the penetration testing session"""
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('pentest_agent')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler - detailed logs
    detailed_log_file = log_path / f"pentest_detailed_{session_id}.log"
    file_handler = logging.FileHandler(detailed_log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # File handler - actions only (for audit trail)
    actions_log_file = log_path / f"pentest_actions_{session_id}.log"
    actions_handler = logging.FileHandler(actions_log_file)
    actions_handler.setLevel(logging.WARNING)  # Only warnings and errors
    actions_handler.setFormatter(detailed_formatter)
    logger.addHandler(actions_handler)
    
    # Log the start of session
    logger.info(f"Penetration testing session started - ID: {session_id}")
    logger.info(f"Detailed logs: {detailed_log_file}")
    logger.info(f"Actions log: {actions_log_file}")
    
    return logger
