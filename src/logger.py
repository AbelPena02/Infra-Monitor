import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("infra_monitor")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("infra_monitor.log", maxBytes=5*1024*1024, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
