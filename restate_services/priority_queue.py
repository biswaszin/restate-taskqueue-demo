from typing import Dict, List, Optional, Any


class PriorityQueueStore:
    def __init__(self):
        self.queue: List[Dict[str, Any]] = []
        self.total_enqueued = 0
        self.total_dequeued = 0

    def enqueue(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.queue.append(task)
        self.queue.sort(key=lambda t: (-t["priority"], t["created_at"]))
        self.total_enqueued += 1
        return {"queue_length": len(self.queue)}

    def dequeue_next(self) -> Optional[Dict[str, Any]]:
        if not self.queue:
            return None
        task = self.queue.pop(0)
        self.total_dequeued += 1
        return task

    def stats(self) -> Dict[str, Any]:
        tier_counts = {"tier1": 0, "tier2": 0, "tier3": 0, "free": 0}
        for t in self.queue:
            tier_counts[t["tier"]] += 1
        return {
            "queue_length": len(self.queue),
            "total_enqueued": self.total_enqueued,
            "total_dequeued": self.total_dequeued,
            "tier_counts": tier_counts,
            "peek": self.queue[0] if self.queue else None,
        }
