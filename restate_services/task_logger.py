from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Dict, Any

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
TASK_LOG_FILE = LOG_DIR / "tasks.log"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_task_event(task_id: str, event: str, payload: Dict[str, Any] | None = None) -> None:
    record = {
        "ts": _utc_now(),
        "task_id": task_id,
        "event": event,
        "payload": payload or {},
    }
    with open(TASK_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
