from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class LocalMemory:
    """Durable local memory; model context is reconstructed from these files."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.conversation_dir = data_dir / "conversations"
        self.memory_dir = data_dir / "memory"
        for directory in (self.conversation_dir, self.memory_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def record(self, task: str, request: dict[str, Any], response: dict[str, Any]) -> Path:
        path = self.conversation_dir / f"{datetime.now():%Y-%m-%d}.jsonl"
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": task,
            "request": request,
            "response": response,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return path

    def context(self, limit: int = 12) -> str:
        summary = self.memory_dir / "rolling_summary.md"
        parts: list[str] = []
        if summary.exists():
            parts.append(summary.read_text(encoding="utf-8"))

        events: list[dict[str, Any]] = []
        for path in sorted(self.conversation_dir.glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        for event in events[-limit:]:
            text = event.get("response", {}).get("text", "")
            parts.append(f"Task: {event.get('task')}\nResult: {text[:3000]}")
        return "\n\n".join(parts)

