# Restate Task Queue Demo (FastAPI)

A priority-based task queue demo with tiered processing (`tier1`, `tier2`, `tier3`, `free`) built with FastAPI.

---

## 1) Setup for new users

### Prerequisites
- Python 3.10+ (recommended: 3.11/3.12)
- `pip`
- Linux/macOS shell (Windows PowerShell equivalents also work)

### Clone and enter project
```bash
git clone <YOUR_REPO_URL>
cd restate-taskqueue-demo
```

### Create virtual environment and install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Create required directories
```bash
mkdir -p logs storage/uploads storage/outputs/json storage/outputs/xml scripts
touch logs/tasks.log
```

---

## 2) Run the server

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server URLs:
- API base: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Quick health check:
```bash
curl -s http://localhost:8000/health | python -m json.tool
```

---

## 3) Use Python script to generate users/tasks

This script creates random users with random tiers and uploads files through `/upload`.

```bash
source .venv/bin/activate
python scripts/generate_users.py --count 25 --base-url http://localhost:8000
```

Options:
- `--count` (required): number of users/tasks to create
- `--base-url` (optional): API URL (default `http://localhost:8000`)
- `--filename-prefix` (optional): uploaded filename prefix

Example:
```bash
python scripts/generate_users.py --count 100 --filename-prefix demo_file
```

---

## 4) Check full queue status (`/queue/all`)

### Endpoint
```bash
curl -s http://localhost:8000/queue/all | python -m json.tool
```

Returns all queued tasks grouped by tier:
- `tier1`
- `tier2`
- `tier3`
- `free`

You can also view queue totals:
```bash
curl -s http://localhost:8000/queue/stats | python -m json.tool
```

---

## 5) Check individual task status by `task_id`

```bash
curl -s http://localhost:8000/tasks/<TASK_ID> | python -m json.tool
```

Example:
```bash
curl -s http://localhost:8000/tasks/ec626abf-f23e-4a76-b77d-17c6028fff11 | python -m json.tool
```

---

## 6) Process tasks with `/worker/tick`

Each tick processes **one** task based on priority logic.

```bash
curl -s -X POST http://localhost:8000/worker/tick | python -m json.tool
```

Run repeatedly until:
```json
{"status":"no_tasks"}
```

### Optional: process everything automatically
If `scripts/process_all.py` exists:
```bash
python scripts/process_all.py
```

---

## 7) Check output files

After processing, converted/AI outputs are written here:

- JSON outputs: `storage/outputs/json/`
- XML outputs: `storage/outputs/xml/`
- Uploaded input files: `storage/uploads/`

Commands:
```bash
ls -lah storage/uploads
ls -lah storage/outputs/json
ls -lah storage/outputs/xml
```

---

## Useful extras

### Watch logs
```bash
tail -f logs/tasks.log
```

If missing:
```bash
mkdir -p logs && touch logs/tasks.log
```

### Clean reset for a fresh demo
```bash
rm -f storage/uploads/*
rm -f storage/outputs/json/*
rm -f storage/outputs/xml/*
rm -f logs/tasks.log
touch logs/tasks.log
```

Then restart server to reset in-memory queue/state.

---

## Notes

- Current implementation is FastAPI-based queue orchestration.
- Queue/status state is in-memory (reset on server restart).
- This repo includes helper scripts for demo speed and repeatability.
