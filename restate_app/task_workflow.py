from typing import Any, Dict
from restate_app.queue_service import queue_service
from restate_app.status_service import status_service
from mocks.ldx_mock import run_mock_convert
from mocks.ai_mock import run_mock_ai
from pathlib import Path
from app.config import JSON_OUT_DIR, XML_OUT_DIR


class TaskWorkflow:
    def run_one(self) -> Dict[str, Any]:
        task = queue_service.dequeue_next()
        if not task:
            return {"status": "no_tasks"}

        task_id = task.task_id
        try:
            status_service.set_status(task_id, "processing:convert")
            convert_out = run_mock_convert(
                    task_id=task_id,
                    original_filename=task.original_filename,
                    json_dir=Path(JSON_OUT_DIR),
                    xml_dir=Path(XML_OUT_DIR),
            )
            status_service.set_convert_output(task_id, convert_out)

            status_service.set_status(task_id, "processing:ai")
            ai_out = run_mock_ai(
                task_id=task_id,
                json_path=convert_out["json_path"],
            )
            status_service.set_ai_output(task_id, ai_out)

            status_service.mark_completed(task_id)

            return {
                "status": "completed",
                "task_id": task_id,
                "result": ai_out,
            }

        except Exception as e:
            status_service.mark_failed(task_id, str(e))
            return {"status": "failed", "task_id": task_id, "error": str(e)}


task_workflow = TaskWorkflow()
