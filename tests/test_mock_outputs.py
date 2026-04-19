from pathlib import Path
from mocks.ldx_mock import run_mock_convert

def test_mock_convert_creates_files(tmp_path: Path):
    json_dir = tmp_path / "json"
    xml_dir = tmp_path / "xml"
    json_dir.mkdir(parents=True, exist_ok=True)
    xml_dir.mkdir(parents=True, exist_ok=True)

    out = run_mock_convert("task-123", "contract.pdf", json_dir, xml_dir)

    assert Path(out["json_path"]).exists()
    assert Path(out["xml_path"]).exists()
    assert out["clause_count"] == 2
    assert out["annotation_count"] == 2
