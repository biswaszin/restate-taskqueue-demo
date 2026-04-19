from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

from app.config import UPLOADS_DIR
from restate_services.models import VALID_TIERS
from restate_services.queue_service import (
    submit_task,
    process_next_task,
    get_task_status,
    get_queue_stats,
)

app = FastAPI(title="Restate Task Queue Demo", version="1.0.0")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    tier: str = Form(...)
):
    tier = tier.strip().lower()
    if tier not in VALID_TIERS:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Use one of: {sorted(VALID_TIERS)}")

    safe_name = file.filename.replace("/", "_")
    local_path = UPLOADS_DIR / safe_name

    with open(local_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    res = submit_task(
        user_id=user_id,
        tier=tier,
        file_path=str(local_path),
        original_filename=file.filename,
    )
    return JSONResponse(status_code=202, content=res)


@app.post("/worker/tick")
def worker_tick():
    return process_next_task()


@app.get("/tasks/{task_id}")
def task_status(task_id: str):
    return get_task_status(task_id)


@app.get("/queue/stats")
def queue_stats():
    return get_queue_stats()
