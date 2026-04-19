from restate_services.queue_service import submit_task, process_next_task, get_task_status

def test_status_flow_end_to_end(tmp_path, monkeypatch):
    # Use default stores; just run one task end-to-end
    res = submit_task("user-1", "tier1", "/tmp/sample.pdf", "sample.pdf")
    task_id = res["task_id"]

    before = get_task_status(task_id)
    assert before["status"] == "queued"

    run = process_next_task()
    assert run["status"] in ("completed", "failed")

    after = get_task_status(task_id)
    assert after["status"] in ("completed", "failed")
