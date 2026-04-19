from typing import Dict, Any, Optional
import time
from restate_services.task_logger import log_task_event


class TaskTrackerStore:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def init_task(self, task: Dict[str, Any]) -> None:
        self.tasks[task["task_id"]] = {
            **task,
            "convert_output": None,
            "ai_output": None,
            "error": None,
            "started_at": None,
            "completed_at": None,
            "updated_at": time.time(),
        }
        log_task_event(task["task_id"], "task_initialized", {
            "tier": task["tier"],
            "priority": task["priority"],
            "user_id": task["user_id"],
            "file_path": task["file_path"],
        })

    def set_status(self, task_id: str, status: str) -> None:
        self._ensure(task_id)
        old_status = self.tasks[task_id]["status"]
        self.tasks[task_id]["status"] = status
        if status == "processing:convert":
            self.tasks[task_id]["started_at"] = time.time()
        self.tasks[task_id]["updated_at"] = time.time()
        log_task_event(task_id, "status_changed", {"from": old_status, "to": status})

    def set_convert_output(self, task_id: str, data: Dict[str, Any]) -> None:
        self._ensure(task_id)
        self.tasks[task_id]["convert_output"] = data
        self.tasks[task_id]["updated_at"] = time.time()
        log_task_event(task_id, "convert_output_saved", data)

    def set_ai_output(self, task_id: str, data: Dict[str, Any]) -> None:
        self._ensure(task_id)
        self.tasks[task_id]["ai_output"] = data
        self.tasks[task_id]["updated_at"] = time.time()
        log_task_event(task_id, "ai_output_saved", {
            "summary": data.get("summary"),
            "confidence": data.get("confidence"),
            "risk_flags_count": len(data.get("risk_flags", [])),
        })

    def mark_completed(self, task_id: str) -> None:
        self._ensure(task_id)
        self.tasks[task_id]["status"] = "completed"
        self.tasks[task_id]["completed_at"] = time.time()
        self.tasks[task_id]["updated_at"] = time.time()
        log_task_event(task_id, "task_completed", {
            "completed_at": self.tasks[task_id]["completed_at"]
        })

    def mark_failed(self, task_id: str, error: str) -> None:
        self._ensure(task_id)
        self.tasks[task_id]["status"] = "failed"
        self.tasks[task_id]["error"] = error
        self.tasks[task_id]["updated_at"] = time.time()
        log_task_event(task_id, "task_failed", {"error": error})

    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)

    def _ensure(self, task_id: str):
        if task_id not in self.tasks:
            raise KeyError(f"Task not found: {task_id}")
