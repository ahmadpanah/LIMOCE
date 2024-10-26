# src/utils/logging_config.py
import logging
import sys
from typing import Optional

def setup_logging(log_level: str = "INFO", 
                 log_file: Optional[str] = None) -> logging.Logger:
    """Configure logging for LIMOCE."""
    logger = logging.getLogger("limoce")
    logger.setLevel(getattr(logging, log_level.upper()))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger