import logging
import logging.handlers
import sys


from minesweeper import PACKAGE_NAME
from minesweeper.config import config


def setup_logger():
    log_config = config['app']['logging']
    logger = logging.getLogger(PACKAGE_NAME)
    logger.setLevel(log_config['level'])
    formatter = logging.Formatter(
        fmt=log_config['msg_format'],
        datefmt=log_config['date_format'],
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
