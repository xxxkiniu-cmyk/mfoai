import logging
import os
from core.config import LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)

class Logger:
    def __init__(self, name="mfo"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            fh = logging.FileHandler(os.path.join(LOG_DIR, "mfo.log"), encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    @classmethod
    def log(cls, name, level, cost, msg, **kwargs):
        inst = cls(name)
        full_msg = f"[{level}] (cost: {cost}) {msg} {kwargs}"
        if level.upper() == "ERROR":
            inst.error(full_msg)
        elif level.upper() == "WARNING":
            inst.warning(full_msg)
        else:
            inst.info(full_msg)
