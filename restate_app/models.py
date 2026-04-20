from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import time
import uuid

VALID_TIERS = {"tier1", "tier2", "tier3", "free"}
TIER_PRIORITY = {"tier1": 1000, "tier2": 900, "tier3": 800, "free": 100}


class TaskPayload(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tier: str
    priority: int
    created_at: float = Field(default_factory=time.time)
    file_path: str
    original_filename: str
    status: str = "queued"


class TaskState(BaseModel):
    task_id: str
    user_id: str
    tier: str
    priority: int
    created_at: float
    file_path: str
    original_filename: str
    status: str = "queued"
    convert_output: Optional[Dict[str, Any]] = None
    ai_output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
