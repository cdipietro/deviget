import logging
import logging.handlers
import sys

from minesweeper import PACKAGE_NAME
from minesweeper.config import config


def setup_logger():
    """Creates a logger object that logs entries in the sinks specified by the `logging` variable from the
    configuration file.

    :param name: The name to be assigned to the returned logger
    :type name: string
    :param config: An object holding the application configuration parameters
    :type config: dict

    :return: A logger object that logs to its own logfile
    :rtype: logging.Logger
    """

    # Disable logging from third-party libraries
    disable_libs_logging()

    # Create the logger
    logger = logging.getLogger(PACKAGE_NAME)
    log_config = config['app']['logging']

    # Set the log level to LOG_LEVEL
    logger.setLevel(log_config['level'])

    # Make a formatter for each log message
    formatter = logging.Formatter(
        fmt=log_config['msg_format'],
        datefmt=log_config['date_format'],
    )

    stdout_config = log_config['sinks'].get('stdout')
    if stdout_config:
        # Make a handler that writes to stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logfile_config = log_config['sinks'].get('file')
    if logfile_config:
        # Make a handler that writes to a file, rotates the entries and keeps backups
        rotated_file_handler = logging.handlers.RotatingFileHandler(
            logfile_config['filename'],
            maxBytes=int(logfile_config['max_size']),
            backupCount=logfile_config['backup_count']
        )
        rotated_file_handler.setFormatter(formatter)
        logger.addHandler(rotated_file_handler)

    return logger


def get_app_logger():
    """Retrieves the main app logger by the app name specified in the configuration file.

    :return: A logger object that matches the given name
    :rtype: logging.Logger
    """
    return logging.getLogger(PACKAGE_NAME)


def disable_libs_logging():
    """'Disables' logging from several libraries by setting the loging level to critical.
    """
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
