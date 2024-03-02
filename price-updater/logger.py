import logging
import os

log_dir = "./log"
log_name = os.getcwd()
log_filename = os.path.basename(log_name)

os.makedirs(log_dir, exist_ok=True)

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(
    format=log_format,
    level=logging.INFO,
    filename=os.path.join(log_dir, log_filename + ".log"),
)

logger = logging.getLogger("Crypto Price Updater")
