import logging
import os
import sys

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

root_logger = logging.getLogger()
root_logger.handlers = []

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(logging.Formatter(log_format))
root_logger.addHandler(stdout_handler)

logger = logging.getLogger("Crypto Price Updater")
