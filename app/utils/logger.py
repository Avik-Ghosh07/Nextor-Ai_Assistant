"""
Logging Configuration
"""

import logging
import sys
import os


def setup_logging():
    """Configure application logging with UTF-8 encoding for emoji support"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure stream handler for console output with UTF-8 encoding
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    
    # Force UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            # Try to reconfigure stdout with UTF-8
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            # Python < 3.7 fallback
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    # Configure file handler for log file
    file_handler = logging.FileHandler('logs/nextor.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[stream_handler, file_handler]
    )
