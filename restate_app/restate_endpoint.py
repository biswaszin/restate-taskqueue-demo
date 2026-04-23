try:
    from restate import Endpoint
except Exception:
    from restate.endpoint import Endpoint  # type: ignore

from restate_app.restate_service import task_service

endpoint = Endpoint()
endpoint.bind(task_service)
app = endpoint.app()
