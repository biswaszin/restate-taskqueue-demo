from typing import Any, Dict, Optional
from restate_app.models import TaskPayload, TaskState


class StatusService:
    """
    In-Restate durable status service wrapper.
    The Restate runtime stores state via the context store APIs in handlers.
    """

    def __init__(self):
        self._mem: Dict[str, TaskState] = {}  # fallback local cache for demo simplicity

    def init_task(self, task: TaskPayload) -> Dict[str, Any]:
        state = TaskState(**task.model_dump())
        self._mem[task.task_id] = state
        return {"ok": True, "task_id": task.task_id}

    def set_status(self, task_id: str, status: str) -> Dict[str, Any]:
        t = self._mem.get(task_id)
        if not t:
            return {"ok": False, "error": "task_not_found"}
        t.status = status
        return {"ok": True}

    def set_convert_output(self, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        t = self._mem.get(task_id)
        if not t:
            return {"ok": False, "error": "task_not_found"}
        t.convert_output = data
        return {"ok": True}

    def set_ai_output(self, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        t = self._mem.get(task_id)
        if not t:
            return {"ok": False, "error": "task_not_found"}
        t.ai_output = data
        return {"ok": True}

    def mark_completed(self, task_id: str) -> Dict[str, Any]:
        t = self._mem.get(task_id)
        if not t:
            return {"ok": False, "error": "task_not_found"}
        t.status = "completed"
        return {"ok": True}

    def mark_failed(self, task_id: str, error: str) -> Dict[str, Any]:
        t = self._mem.get(task_id)
        if not t:
            return {"ok": False, "error": "task_not_found"}
        t.status = "failed"
        t.error = error
        return {"ok": True}

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        t = self._mem.get(task_id)
        return t.model_dump() if t else None


status_service = StatusService()
