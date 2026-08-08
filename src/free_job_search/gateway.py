from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


class GatewayError(RuntimeError):
    def __init__(self, message: str, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


@dataclass
class AnthropicGateway:
    base_url: str
    api_key: str
    timeout_seconds: int = 90

    def health(self) -> tuple[int, str]:
        request = urllib.request.Request(f"{self.base_url}/health", method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return response.status, response.read().decode("utf-8", errors="replace")
        except urllib.error.URLError as exc:
            raise GatewayError(f"OmniRoute is unreachable: {exc}", retryable=True) from exc

    def messages(self, model: str, system: str, user: str, max_tokens: int = 4096) -> dict:
        payload = {
            "model": model,
            "system": system,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user}],
        }
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            f"{self.base_url}/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                result = json.loads(response.read().decode("utf-8"))
                result["_request"] = payload
                return result
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise GatewayError(f"Gateway HTTP {exc.code}: {body[:500]}", retryable=exc.code in {408, 429, 500, 502, 503, 504}) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise GatewayError(f"Gateway request failed: {exc}", retryable=True) from exc

    @staticmethod
    def text(response: dict) -> str:
        return "\n".join(
            block.get("text", "")
            for block in response.get("content", [])
            if block.get("type") == "text"
        ).strip()
