# core/logger.py

import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Set up basic logging configuration
logging.basicConfig(
    filename=f"{LOG_DIR}/matrix_{datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    """Log an info-level message"""
    logging.info(message)

def log_error(message):
    """Log an error-level message"""
    logging.error(message)