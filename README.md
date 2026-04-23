# Restate Task Queue Demo

A durable **priority task queue** built with **Python + Restate Virtual Objects**.

This project lets you:

- Enqueue tasks (single or batch)
- Persist queue/task state durably in Restate
- Process tasks by priority (`tier1 > tier2 > tier3 > free`)
- Generate output artifacts (`JSON` and `XML`)
- Track execution via `logs/bifrost.log`

---

## 1) Project Architecture

### Core components

- `restate_app/restate_endpoint.py`
  - Creates Restate endpoint and binds the `TaskService` virtual object.
- `restate_app/restate_service.py`
  - Contains all queue handlers and business logic.
- `storage/uploads/`
  - Raw input files created during enqueue.
- `storage/outputs/json/`
  - Processed JSON artifacts.
- `storage/outputs/xml/`
  - Processed XML artifacts.
- `logs/bifrost.log`
  - Local application log (`QUEUED`, `DONE`, `TICK`, etc).

### State model (inside Restate object state)

For each object key (example: `global`):

- `queue/index` → list of `task_id`s
- `task/<task_id>` → full task record:
  - `task_id`, `user_id`, `tier`, `priority`
  - `status` (`queued` / `completed`)
  - `input_path`, `json_path`, `xml_path`
  - timestamps (`created_at`, `completed_at`)

Each **object key** is an isolated queue namespace.  
If you use a new key (e.g. `global-v2`), you get a fresh queue.

---

## 2) Prerequisites

- Python 3.10+ (recommended)
- `pip`
- Restate CLI / server available in PATH
- Linux/macOS/WSL terminal

---

## 3) Local Setup

```bash
git clone https://github.com/biswaszin/restate-taskqueue-demo.git
cd restate-taskqueue-demo

python3 -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt
# If requirements.txt is missing/incomplete:
# pip install restate-sdk hypercorn
```

Verify SDK import:

```bash
python -c "import restate; print('restate sdk ok')"
```

---

## 4) Start Services

Use 3 terminals.

### Terminal A — start Restate server

```bash
restate-server
```

UI will be available at:

- `http://localhost:9070`

---

### Terminal B — start endpoint app

```bash
cd /path/to/restate-taskqueue-demo
source .venv/bin/activate
PYTHONPATH=. python -m hypercorn restate_app.restate_endpoint:app --bind 0.0.0.0:9080 --reload
```

---

### Terminal C — register deployment

```bash
restate deployments register http://localhost:9080
restate deployments list
```

---

## 5) Invoke End-to-End Flow (from UI)

Open `http://localhost:9070`, find `TaskService`.

> Important: for every call, set `key*` (required), e.g. `global`.

### Step 1 — `enqueue_batch`

- Handler: `enqueue_batch`
- Parameter: `key* = global`
- Body:

```json
{
  "users": [
    {
      "user_id": "u1",
      "tier": "tier2",
      "tasks": [
        {"filename": "u1_a.txt", "content": "task A"},
        {"filename": "u1_b.txt", "content": "task B"}
      ]
    },
    {
      "user_id": "u2",
      "tier": "tier1",
      "tasks": [
        {"filename": "u2_vip.txt", "content": "vip task"}
      ]
    },
    {
      "user_id": "u3",
      "tier": "free",
      "tasks": [
        {"filename": "u3_free.txt", "content": "free task"}
      ]
    }
  ]
}
```

Expected response shape:

```json
{
  "ok": true,
  "created_count": 4,
  "task_ids": ["...", "...", "...", "..."]
}
```

---

### Step 2 — `list`

- Handler: `list`
- Parameter: `key* = global`
- Body: `{}`

Expected:

- `count` = number of queued + completed tasks currently in this key’s queue index.
- Initially after enqueue (fresh key): `count: 4`, statuses mostly `queued`.

---

### Step 3 — `tick`

- Handler: `tick`
- Parameter: `key* = global`
- Body:

```json
{"max_items": 10}
```

Expected:

```json
{
  "ok": true,
  "processed_count": 4,
  "processed_task_ids": ["...", "...", "...", "..."]
}
```

---

### Step 4 — `results`

- Handler: `results`
- Parameter: `key* = global`
- Body: `{}`

Expected summary after successful tick:

- `total: 4`
- `completed: 4`
- `queued: 0`

---

### Step 5 (optional) — `get`

- Handler: `get`
- Parameter: `key* = global`
- Body:

```json
{"task_id":"<one-task-id>"}
```

Expected task should show:

- `status: "completed"`
- non-empty `json_path` and `xml_path`

---

## 6) Quick Verification

### Check generated files

```bash
ls -lah storage/uploads
ls -lah storage/outputs/json
ls -lah storage/outputs/xml
```

### Check logs

```bash
tail -n 100 logs/bifrost.log
```

You should see lines like:

- `QUEUED ...`
- `DONE ...`
- `TICK processed_count=...`

### Check priority behavior

Enqueue mixed tiers and run `tick` with small `max_items` (e.g. 2).  
Expected processing order: `tier1` first, then `tier2`, `tier3`, `free`.

---

## 7) Common Issues & Fixes

### “You didn’t provide all required parameters”
- You missed `key*` in UI.
- Set `key*` to e.g. `global`.

### “count is too high (old tasks still there)”
- You reused the same object key (`global`).
- Use a new key (`global-v2`) for a fresh queue namespace.

### “Import restate could not be resolved”
- Wrong Python interpreter in IDE.
- Activate `.venv` and select it in VS Code.

### Invocation succeeded but body not visible in UI
- Open invocation details to inspect output.
- Also verify endpoint logs in Terminal B.
- Ensure endpoint app is running on `:9080` and deployment re-registered after code changes.

---

## 8) Useful cURL (direct endpoint testing)

```bash
curl -v --request POST \
  --url http://localhost:9080/TaskService/global/list \
  --header 'Content-Type: application/json' \
  --data '{}'
```

```bash
curl -v --request POST \
  --url http://localhost:9080/TaskService/global/tick \
  --header 'Content-Type: application/json' \
  --data '{"max_items":10}'
```

---

## 9) Refresh / Run Again from Clean-ish Start

If you want to run again quickly without touching Restate internals:

1. Use a new key (`global-2`, `global-3`, …).
2. Clear local generated artifacts/logs (optional):

```bash
rm -rf storage/uploads storage/outputs logs
mkdir -p storage/uploads storage/outputs/json storage/outputs/xml logs
touch logs/bifrost.log
```

3. Re-run flow (`enqueue_batch -> list -> tick -> results`) with the new key.

---

## 10) Full Reset (including durable state)

If you also want to clear Restate persisted state, stop `restate-server`, remove its storage directory, then restart and re-register deployment.

> Tip: run Restate with an explicit storage dir so reset is easy:
>
> ```bash
> restate-server --storage-dir .restate-data
> ```
>
> Then full reset:
>
> ```bash
> # stop restate-server first
> rm -rf .restate-data
> restate-server --storage-dir .restate-data
> restate deployments register http://localhost:9080
> ```

(If your version uses a different flag name, check `restate-server --help`.)

---

## 11) Development Notes

- Keep handler signatures consistent, e.g. `async def handler(ctx, req=None)`.
- Always use the same key through one test run.
- Re-register deployment after significant endpoint changes.

---

Happy queueing 🚀
