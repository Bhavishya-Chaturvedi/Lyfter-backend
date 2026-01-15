import json
import logging
import os
from datetime import datetime

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=LOG_LEVEL)

logger = logging.getLogger("app")


def log_json(**fields):
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        **fields,
    }

    logger.log(
        logging.INFO,
        json.dumps(record, ensure_ascii=False)
    )
