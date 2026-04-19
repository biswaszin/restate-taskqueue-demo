import json
import time
from typing import Dict, Any


def run_mock_ai(task_id: str, json_path: str) -> Dict[str, Any]:
    """
    Simulate AI processing for legal analysis.
    """
    time.sleep(1.2)

    with open(json_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    return {
        "task_id": task_id,
        "summary": f"Analyzed {doc.get('source_file')} with {doc['counts']['clauses']} clauses.",
        "risk_flags": [
            "Termination notice period may be commercially unfavorable.",
            "Payment timeline may require stricter penalty language."
        ],
        "confidence": 0.93,
        "recommendations": [
            "Add late payment penalty clause.",
            "Shorten termination notice from 60 to 30 days."
        ]
    }
