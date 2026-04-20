from fastapi import FastAPI
from restate_app.queue_service import queue_service
from restate_app.status_service import status_service
from restate_app.task_workflow import task_workflow

# NOTE:
# This exposes a service HTTP endpoint.
# You can register this URL in Restate deployment discovery.
app = FastAPI(title="Restate Service Endpoint", version="1.0.0")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/discover")
def discover():
    return {
        "services": [
            "queue_service",
            "status_service",
            "task_workflow"
        ]
    }
