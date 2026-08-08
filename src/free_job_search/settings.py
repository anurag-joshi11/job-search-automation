from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path



def load_dotenv_fallback(path: Path = Path(".env")) -> None:
    """Load simple KEY=VALUE entries without requiring a third-party package."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    config_path: Path
    data_dir: Path
    timeout_seconds: int

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv_fallback()
        return cls(
            base_url=os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128").rstrip("/"),
            api_key=os.getenv("OMNIROUTE_API_KEY", ""),
            config_path=Path(os.getenv("JOB_SEARCH_CONFIG", "config/models.json")),
            data_dir=Path(os.getenv("JOB_SEARCH_DATA_DIR", "data")),
            timeout_seconds=int(os.getenv("JOB_SEARCH_TIMEOUT_SECONDS", "90")),
        )

    def load_model_config(self) -> dict:
        return json.loads(self.config_path.read_text(encoding="utf-8"))
