from dataclasses import dataclass, asdict
from typing import Dict, Any
import time
import uuid

TIER_PRIORITY = {
    "tier1": 1000,
    "tier2": 500,
    "tier3": 100,
    "free": 1,
}

VALID_TIERS = set(TIER_PRIORITY.keys())


@dataclass
class Task:
    task_id: str
    user_id: str
    tier: str
    priority: int
    created_at: float
    file_path: str
    original_filename: str
    status: str = "queued"

    @staticmethod
    def create(user_id: str, tier: str, file_path: str, original_filename: str) -> "Task":
        return Task(
            task_id=str(uuid.uuid4()),
            user_id=user_id,
            tier=tier,
            priority=TIER_PRIORITY[tier],
            created_at=time.time(),
            file_path=file_path,
            original_filename=original_filename,
            status="queued",
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
