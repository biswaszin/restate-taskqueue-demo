from restate_services.priority_queue import PriorityQueueStore

def test_priority_and_fifo_sorting():
    q = PriorityQueueStore()

    q.enqueue({"task_id": "free1", "tier": "free", "priority": 1, "created_at": 100})
    q.enqueue({"task_id": "t1_a", "tier": "tier1", "priority": 1000, "created_at": 200})
    q.enqueue({"task_id": "t1_b", "tier": "tier1", "priority": 1000, "created_at": 210})
    q.enqueue({"task_id": "t2", "tier": "tier2", "priority": 500, "created_at": 50})

    assert q.dequeue_next()["task_id"] == "t1_a"
    assert q.dequeue_next()["task_id"] == "t1_b"
    assert q.dequeue_next()["task_id"] == "t2"
    assert q.dequeue_next()["task_id"] == "free1"
