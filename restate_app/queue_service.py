from typing import Any, Dict, List, Optional
from restate_app.models import TaskPayload, VALID_TIERS, TIER_PRIORITY


class QueueService:
    def __init__(self):
        self.tier_queues: Dict[str, List[TaskPayload]] = {
            "tier1": [],
            "tier2": [],
            "tier3": [],
            "free": [],
        }
        self.total_enqueued = 0
        self.total_dequeued = 0

    def submit_task(self, task: TaskPayload) -> Dict[str, Any]:
        if task.tier not in VALID_TIERS:
            return {"ok": False, "error": "invalid_tier"}

        self.tier_queues[task.tier].append(task)
        self.total_enqueued += 1
        return {
            "ok": True,
            "task_id": task.task_id,
            "status": "queued",
            "priority": task.priority,
        }

    def dequeue_next(self) -> Optional[TaskPayload]:
        for tier in ["tier1", "tier2", "tier3", "free"]:
            if self.tier_queues[tier]:
                self.total_dequeued += 1
                return self.tier_queues[tier].pop(0)
        return None

    def stats(self) -> Dict[str, Any]:
        queue_length = sum(len(v) for v in self.tier_queues.values())
        peek = None
        for tier in ["tier1", "tier2", "tier3", "free"]:
            if self.tier_queues[tier]:
                peek = self.tier_queues[tier][0].model_dump()
                break

        return {
            "queue_length": queue_length,
            "total_enqueued": self.total_enqueued,
            "total_dequeued": self.total_dequeued,
            "tier_counts": {k: len(v) for k, v in self.tier_queues.items()},
            "peek": peek,
        }


    def list_all_tasks(self):
        return {
             "tier1": [t.model_dump() for t in self.tier_queues["tier1"]],
             "tier2": [t.model_dump() for t in self.tier_queues["tier2"]],
             "tier3": [t.model_dump() for t in self.tier_queues["tier3"]],
             "free":  [t.model_dump() for t in self.tier_queues["free"]],
    }

    @staticmethod
    def build_task(user_id: str, tier: str, file_path: str, original_filename: str) -> TaskPayload:
        return TaskPayload(
            user_id=user_id,
            tier=tier,
            priority=TIER_PRIORITY[tier],
            file_path=file_path,
            original_filename=original_filename,
        )


queue_service = QueueService()
