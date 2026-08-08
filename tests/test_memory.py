from pathlib import Path

from free_job_search.memory import LocalMemory


def test_memory_records_and_loads_context(tmp_path: Path) -> None:
    memory = LocalMemory(tmp_path / "data")
    memory.record("rank", {"prompt": "job"}, {"text": "strong fit"})
    assert "strong fit" in memory.context()

