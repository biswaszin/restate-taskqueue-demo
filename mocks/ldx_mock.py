import json
import time
from pathlib import Path
from typing import Dict, Any


def run_mock_convert(task_id: str, original_filename: str, json_dir: Path, xml_dir: Path) -> Dict[str, Any]:
    """
    Simulate converting uploaded legal file into JSON + XML artifacts.
    """
    time.sleep(1.2)

    json_path = json_dir / f"{task_id}.json"
    xml_path = xml_dir / f"{task_id}.xml"

    payload = {
        "task_id": task_id,
        "source_file": original_filename,
        "document_type": "legal_contract",
        "clauses": [
            {"clause_id": "C1", "title": "Payment Terms", "text": "Payment due in 30 days."},
            {"clause_id": "C2", "title": "Termination", "text": "Either party may terminate with 60 days notice."},
        ],
        "annotations": [
            {"id": "A1", "label": "Risk", "note": "Termination window is long."},
            {"id": "A2", "label": "Obligation", "note": "Buyer must pay within 30 days."},
        ],
        "counts": {"clauses": 2, "annotations": 2},
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<legalDocument taskId="{task_id}" source="{original_filename}">
  <clauses>
    <clause id="C1" title="Payment Terms">Payment due in 30 days.</clause>
    <clause id="C2" title="Termination">Either party may terminate with 60 days notice.</clause>
  </clauses>
  <annotations>
    <annotation id="A1" label="Risk">Termination window is long.</annotation>
    <annotation id="A2" label="Obligation">Buyer must pay within 30 days.</annotation>
  </annotations>
</legalDocument>
"""
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    return {
        "json_path": str(json_path),
        "xml_path": str(xml_path),
        "clause_count": 2,
        "annotation_count": 2,
    }
