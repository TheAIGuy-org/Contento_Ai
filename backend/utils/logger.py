import logging
import sys
import os

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: The name of the logger (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if handlers haven't been added yet
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Create console handler with a higher log level
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        ch.setFormatter(formatter)
        
        # Add the handlers to the logger
        logger.addHandler(ch)
        
        # Prevent propagation to root logger to avoid duplicate logs if root is configured
        logger.propagate = False
        
    return logger
