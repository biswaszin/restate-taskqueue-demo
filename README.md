# Restate Task Queue Demo (Python, Simulated)

Demo project showing a priority-based task queue:
- Upload file
- Simulate convert -> `.json` + `.xml`
- Simulate AI processing
- Track task status + queue stats

Priority:
- tier1 > tier2 > tier3 > free
- FIFO within same tier (`created_at`)

---

## 1) Prerequisites

- Ubuntu (or Linux)
- Python 3.11+
- pip
- curl

---

## 2) Setup

```bash
git clone https://github.com/biswaszin/restate-taskqueue-demo.git
cd restate-taskqueue-demo

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3) Run API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

---

## 4) Demo: Upload + Process + Status

### Upload 4 tasks (different tiers)

```bash
# free
curl -X POST http://localhost:8000/upload \
  -F "file=@/etc/hosts" \
  -F "user_id=u_free" \
  -F "tier=free"

# tier3
curl -X POST http://localhost:8000/upload \
  -F "file=@/etc/hosts" \
  -F "user_id=u_t3" \
  -F "tier=tier3"

# tier1
curl -X POST http://localhost:8000/upload \
  -F "file=@/etc/hosts" \
  -F "user_id=u_t1" \
  -F "tier=tier1"

# tier2
curl -X POST http://localhost:8000/upload \
  -F "file=@/etc/hosts" \
  -F "user_id=u_t2" \
  -F "tier=tier2"
```

### Check queue stats

```bash
curl http://localhost:8000/queue/stats
```

### Process one task at a time (manual control)

```bash
curl -X POST http://localhost:8000/worker/tick
curl -X POST http://localhost:8000/worker/tick
curl -X POST http://localhost:8000/worker/tick
curl -X POST http://localhost:8000/worker/tick
```

### Check task status

```bash
curl http://localhost:8000/tasks/<TASK_ID>
```

---

## 5) Verify generated artifacts

After processing:
- `storage/outputs/json/<task_id>.json`
- `storage/outputs/xml/<task_id>.xml`

---

## 6) Run tests

```bash
pytest -q
```

---

## 7) Notes

This is a **demo** implementation (simulated convert + AI).
To make it production:
- replace in-memory stores with durable state
- integrate real ldx-service + ai-service
- add auth/JWT + idempotency keys + retry policies
- add observability/logging stack
