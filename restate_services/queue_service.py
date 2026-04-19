from typing import Dict, Any
from restate_services.models import Task
from restate_services.priority_queue import PriorityQueueStore
from restate_services.task_tracker import TaskTrackerStore
from mocks.ldx_mock import run_mock_convert
from mocks.ai_mock import run_mock_ai
from app.config import JSON_OUT_DIR, XML_OUT_DIR
from restate_services.task_logger import log_task_event

queue_store = PriorityQueueStore()
tracker_store = TaskTrackerStore()


def submit_task(user_id: str, tier: str, file_path: str, original_filename: str) -> Dict[str, Any]:
    
    task = Task.create(
        user_id=user_id,
        tier=tier,
        file_path=file_path,
        original_filename=original_filename,
    ).to_dict()

    tracker_store.init_task(task)
    queue_store.enqueue(task)
    log_task_event(
        task["task_id"],
        "task_enqueued",
        {
            "tier": task["tier"],
            "priority": task["priority"],
            "created_at": task["created_at"],
        },
    )

    print(f"[SUBMIT] task={task['task_id']} tier={tier} priority={task['priority']}")
    return {
        "task_id": task["task_id"],
        "status": "queued",
        "priority": task["priority"],
    }


def process_next_task() -> Dict[str, Any]:

    task = queue_store.dequeue_next()
    if not task:
        return {"status": "no_tasks"}

    task_id = task["task_id"]
    log_task_event(
        task_id,
        "task_dequeued",
        {
             "tier": task["tier"],
            "priority": task["priority"],
        },
)

# restate-taskqueue-demo
    task_id = task["task_id"]
    try:
        print(f"[DEQUEUE] task={task_id} tier={task['tier']} priority={task['priority']}")

        tracker_store.set_status(task_id, "processing:convert")
        print(f"[CONVERT] start task={task_id}")
        convert_output = run_mock_convert(
            task_id=task_id,
            original_filename=task["original_filename"],
            json_dir=JSON_OUT_DIR,
            xml_dir=XML_OUT_DIR,
        )
        tracker_store.set_convert_output(task_id, convert_output)
        print(f"[CONVERT] done task={task_id} json={convert_output['json_path']} xml={convert_output['xml_path']}")

        tracker_store.set_status(task_id, "processing:ai")
        print(f"[AI] start task={task_id}")
        ai_output = run_mock_ai(task_id=task_id, json_path=convert_output["json_path"])
        tracker_store.set_ai_output(task_id, ai_output)
        print(f"[AI] done task={task_id} confidence={ai_output['confidence']}")

        tracker_store.mark_completed(task_id)
        print(f"[DONE] task={task_id}")

        return {"status": "completed", "task_id": task_id, "result": ai_output}
    except Exception as e:
        tracker_store.mark_failed(task_id, str(e))
        print(f"[FAIL] task={task_id} error={e}")
        return {"status": "failed", "task_id": task_id, "error": str(e)}


def get_task_status(task_id: str) -> Dict[str, Any]:
    task = tracker_store.get_status(task_id)
    if not task:
        return {"error": "task_not_found", "task_id": task_id}
    return task


def get_queue_stats() -> Dict[str, Any]:
    return queue_store.stats()
