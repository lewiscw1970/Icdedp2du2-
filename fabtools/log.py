"""
Log
======
"""

import logging

LOG_NAME = 'fabric'
LOG_FILENAME = 'fabric.log'

def setup_logger(name, filename):
    """
    Configure logger
    """
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        handler = logging.FileHandler(filename)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    #    logger.debug(name + ' logger created')
    #else:
    #    logger.debug(name + ' already exists')
    return logger

def write(text=None, name=None, filename=None):
    """
    Write text to logger
    """
    if not name:
        name = LOG_NAME
    if not filename:
        filename = LOG_FILENAME

    logger = setup_logger(name=name, filename=filename)
    logger.debug(text)
