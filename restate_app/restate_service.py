from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid

try:
    from restate import VirtualObject, Context
except Exception:
    from restate import VirtualObject  # type: ignore
    from restate.context import Context  # type: ignore


UPLOADS_DIR = Path("storage/uploads")
JSON_DIR = Path("storage/outputs/json")
XML_DIR = Path("storage/outputs/xml")
LOG_FILE = Path("logs/bifrost.log")

for d in [UPLOADS_DIR, JSON_DIR, XML_DIR, LOG_FILE.parent]:
    d.mkdir(parents=True, exist_ok=True)
LOG_FILE.touch(exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def tier_priority(tier: str) -> int:
    t = (tier or "").lower()
    return {"tier1": 1, "tier2": 2, "tier3": 3}.get(t, 99)


def log_line(message: str) -> None:
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{now_iso()} | {message}\n")


def as_dict(req: Any) -> dict[str, Any]:
    if isinstance(req, dict):
        return req
    if hasattr(req, "__dict__"):
        return dict(req.__dict__)
    return {}


task_service = VirtualObject("TaskService")


@task_service.handler("submit")
async def submit(ctx: Context, req: Any):
    data = as_dict(req)
    user_id = data.get("user_id", "")
    tier = data.get("tier", "tier3")
    filename = data.get("filename", "task.txt")
    content = data.get("content", "")

    task_id = str(uuid.uuid4())
    safe_name = filename.replace("/", "_")
    input_path = UPLOADS_DIR / f"{task_id}_{safe_name}"
    input_path.write_text(content, encoding="utf-8")

    task = {
        "task_id": task_id,
        "user_id": user_id,
        "tier": tier,
        "priority": tier_priority(tier),
        "status": "queued",
        "input_path": str(input_path),
        "json_path": "",
        "xml_path": "",
        "created_at": now_iso(),
        "completed_at": None,
    }

    ctx.set(f"task/{task_id}", task)

    queue_index = await ctx.get("queue/index")
    if queue_index is None:
        queue_index = []
    queue_index.append(task_id)
    ctx.set("queue/index", queue_index)

    log_line(
        f"QUEUED task_id={task_id} user_id={user_id} tier={tier} file={safe_name}"
    )
    return {"ok": True, "task": task}


@task_service.handler("enqueue_batch")
async def enqueue_batch(ctx: Context, req: Any):
    data = as_dict(req)
    users = data.get("users", [])
    created_ids: list[str] = []

    for user in users:
        user_id = user.get("user_id", "")
        tier = user.get("tier", "tier3")
        tasks = user.get("tasks", [])

        for t in tasks:
            out = await submit(
                ctx,
                {
                    "user_id": user_id,
                    "tier": tier,
                    "filename": t.get("filename", "task.txt"),
                    "content": t.get("content", ""),
                },
            )
            created_ids.append(out["task"]["task_id"])

    log_line(f"BATCH_ENQUEUED count={len(created_ids)}")
    return {"ok": True, "created_count": len(created_ids), "task_ids": created_ids}


@task_service.handler("get")
async def get_task(ctx: Context, req: Any):
    data = as_dict(req)
    task_id = data.get("task_id", "")
    task = await ctx.get(f"task/{task_id}")
    if not task:
        return {"ok": False, "error": "task_not_found", "task_id": task_id}
    return {"ok": True, "task": task}


@task_service.handler("list")
async def list_tasks(ctx: Context):
    queue_index = await ctx.get("queue/index")
    if queue_index is None:
        queue_index = []

    tasks = []
    for task_id in queue_index:
        t = await ctx.get(f"task/{task_id}")
        if t:
            tasks.append(t)

    return {"ok": True, "count": len(tasks), "tasks": tasks}


@task_service.handler("process")
async def process(ctx: Context, req: Any):
    data = as_dict(req)
    task_id = data.get("task_id", "")
    task = await ctx.get(f"task/{task_id}")

    if not task:
        return {"ok": False, "error": "task_not_found", "task_id": task_id}

    if task.get("status") == "completed":
        return {"ok": True, "task": task, "note": "already_completed"}

    json_path = JSON_DIR / f"{task_id}.json"
    xml_path = XML_DIR / f"{task_id}.xml"

    payload = {
        "task_id": task_id,
        "user_id": task["user_id"],
        "tier": task["tier"],
        "priority": task["priority"],
        "source_file": task["input_path"],
        "processed_at": now_iso(),
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    xml_path.write_text(
        "<root>\n"
        f"  <task_id>{task_id}</task_id>\n"
        f"  <user_id>{task['user_id']}</user_id>\n"
        f"  <tier>{task['tier']}</tier>\n"
        f"  <priority>{task['priority']}</priority>\n"
        f"  <source_file>{task['input_path']}</source_file>\n"
        "</root>\n",
        encoding="utf-8",
    )

    task["status"] = "completed"
    task["json_path"] = str(json_path)
    task["xml_path"] = str(xml_path)
    task["completed_at"] = now_iso()

    ctx.set(f"task/{task_id}", task)

    log_line(
        f"DONE task_id={task_id} user_id={task['user_id']} "
        f"tier={task['tier']} priority={task['priority']}"
    )
    return {"ok": True, "task": task}


@task_service.handler("tick")
async def tick(ctx: Context, req: Any):
    data = as_dict(req)
    max_items = int(data.get("max_items", 5) or 5)

    queue_index = await ctx.get("queue/index")
    if queue_index is None:
        queue_index = []

    queued_tasks = []
    for task_id in queue_index:
        t = await ctx.get(f"task/{task_id}")
        if t and t.get("status") == "queued":
            queued_tasks.append(t)

    queued_tasks.sort(
        key=lambda t: (t.get("priority", 99), t.get("created_at", ""))
    )
    selected = queued_tasks[: max(1, max_items)]

    processed_ids = []
    for t in selected:
        out = await process(ctx, {"task_id": t["task_id"]})
        if out.get("ok"):
            processed_ids.append(t["task_id"])

    log_line(
        f"TICK processed_count={len(processed_ids)} "
        f"task_ids={processed_ids}"
    )
    return {
        "ok": True,
        "processed_count": len(processed_ids),
        "processed_task_ids": processed_ids,
    }


@task_service.handler("results")
async def results(ctx: Context):
    queue_index = await ctx.get("queue/index")
    if queue_index is None:
        queue_index = []

    completed = []
    queued = []

    for task_id in queue_index:
        t = await ctx.get(f"task/{task_id}")
        if not t:
            continue
        if t.get("status") == "completed":
            completed.append(t)
        else:
            queued.append(t)

    completed.sort(key=lambda t: t.get("completed_at") or "")
    queued.sort(key=lambda t: (t.get("priority", 99), t.get("created_at", "")))

    return {
        "ok": True,
        "summary": {
            "total": len(completed) + len(queued),
            "completed": len(completed),
            "queued": len(queued),
        },
        "completed_tasks": completed,
        "queued_tasks": queued,
        "log_file": str(LOG_FILE),
    }
