#!/usr/bin/env bash
set -euo pipefail

cd /home/biswas/task-queue/restate-taskqueue-demo

rm -rf storage/uploads/* || true
rm -rf storage/outputs/json/* || true
rm -rf storage/outputs/xml/* || true
rm -f logs/tasks.log || true

echo "Demo files/logs cleaned."
echo "Now restart uvicorn to clear in-memory queue/status."
