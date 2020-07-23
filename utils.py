import hashlib
from datetime import datetime


def create_task_id(url: str) -> str:
    md5 = hashlib.md5(url.encode("utf-8")).hexdigest()
    utc = datetime.utcnow()
    return f"{md5[:7]}-{utc.strftime('%y%m%d%H%M%S%f')}"
