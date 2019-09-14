import logging
import logging.handlers
import sys

from minesweeper import PACKAGE_NAME


def setup_logger():
    logger = logging.getLogger(PACKAGE_NAME)
    formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d [%(levelname)-8s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel('DEBUG')
    return logger
