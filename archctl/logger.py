"""Module for setting up logging."""
import logging
import sys

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

LOG_FORMATS = {
    'DEBUG': '%(levelname)s %(name)s: %(message)s',
    'INFO': '%(levelname)s: %(message)s',
}


def setup_logger(stream_level='DEBUG'):
    """Configure logger for archctl
    Set up logging to stdout with given level, defaults to DEBUG.
    """

    # Create logger for archctl moduke
    logger = logging.getLogger('archctl')
    logger.setLevel(logging.DEBUG)

    # Remove all attached handlers, in case there was
    # a logger with using the name 'archctl'
    del logger.handlers[:]

    # Get settings based on the given stream_level
    log_formatter = logging.Formatter(LOG_FORMATS[stream_level])
    log_level = LOG_LEVELS[stream_level]

    # Create a stream handler
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    return logger
