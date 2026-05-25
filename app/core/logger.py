import logging
from pythonjsonlogger import json as jsonlogger

def setup_logger():
    logger = logging.getLogger("api")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()  
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

logger = setup_logger()
