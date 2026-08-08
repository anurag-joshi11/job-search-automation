from pathlib import Path

from free_job_search.memory import LocalMemory
from free_job_search.router import TaskRouter


class FakeGateway:
    def __init__(self) -> None:
        self.calls = []

    def messages(self, model: str, system: str, user: str, max_tokens: int = 4096) -> dict:
        self.calls.append(model)
        return {"content": [{"type": "text", "text": "ok"}], "_request": {"model": model}}

    @staticmethod
    def text(response: dict) -> str:
        return response["content"][0]["text"]


def test_router_selects_task_profile(tmp_path: Path) -> None:
    gateway = FakeGateway()
    config = {
        "profiles": {"fast": {"model": "fast-model", "fallbacks": ["quality"]}, "quality": {"model": "quality-model", "fallbacks": []}},
        "tasks": {"scrape": "fast"},
    }
    result = TaskRouter(gateway, LocalMemory(tmp_path / "data"), config).run("scrape", "hello")
    assert result.profile == "fast"
    assert gateway.calls == ["fast-model"]

