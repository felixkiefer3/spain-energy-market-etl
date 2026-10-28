import logging

def setup_logger():
    """
    Configures and returns a custom logger for the ETL pipeline.
    
    Sets up logging to both a local file ('pipeline.log') and the standard console,
    ensuring all events at INFO level and above are recorded with timestamps.
    
    Returns:
        logging.Logger: The configured logger instance.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pipeline.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)