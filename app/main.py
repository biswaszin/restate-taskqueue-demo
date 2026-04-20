from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil

from app.config import UPLOADS_DIR
from restate_app.models import VALID_TIERS
from restate_app.queue_service import queue_service
from restate_app.status_service import status_service
from restate_app.task_workflow import task_workflow
from pathlib import Path

app = FastAPI(title="Restate Task Queue Demo", version="2.0.0")
Path("logs").mkdir(parents=True, exist_ok=True)
Path("logs/tasks.log").touch(exist_ok=True)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    tier: str = Form(...),
):
    tier = tier.strip().lower()
    if tier not in VALID_TIERS:
        allowed = ", ".join(sorted(VALID_TIERS))
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier. Use one of: {allowed}",
        )

    original_filename = file.filename or "uploaded_file.bin"
    safe_name = original_filename.replace("/", "_")
    local_path = UPLOADS_DIR / safe_name

    with open(local_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    task = queue_service.build_task(
        user_id=user_id,
        tier=tier,
        file_path=str(local_path),
        original_filename=original_filename,
    )

    status_service.init_task(task)
    res = queue_service.submit_task(task)
    return JSONResponse(status_code=202, content=res)


@app.post("/worker/tick")
def worker_tick():
    return task_workflow.run_one()


@app.get("/tasks/{task_id}")
def task_status(task_id: str):
    t = status_service.get_task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t


@app.get("/queue/stats")
def queue_stats():
    return queue_service.stats()

@app.get("/queue/all")
def queue_all():
    return queue_service.list_all_tasks()
