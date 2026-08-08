from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .gateway import AnthropicGateway, GatewayError
from .memory import LocalMemory
from .router import TaskRouter
from .settings import Settings


def build_router() -> tuple[Settings, TaskRouter]:
    settings = Settings.from_environment()
    gateway = AnthropicGateway(settings.base_url, settings.api_key, settings.timeout_seconds)
    return settings, TaskRouter(gateway, LocalMemory(settings.data_dir), settings.load_model_config())


def main() -> int:
    parser = argparse.ArgumentParser(prog="free-job-search")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health", help="check the OmniRoute gateway")

    chat = subparsers.add_parser("chat", help="run one local chat request")
    chat.add_argument("--task", default="general")
    chat.add_argument("prompt", nargs="*")

    rank = subparsers.add_parser("rank", help="rank one saved job description")
    rank.add_argument("--job", required=True, type=Path)

    args = parser.parse_args()
    try:
        settings, router = build_router()
        if args.command == "health":
            status, body = router.gateway.health()
            print(f"OmniRoute: HTTP {status} {body[:300]}")
            return 0

        if args.command == "rank":
            job_text = args.job.read_text(encoding="utf-8")
            prompt = (
                "Rank this job for the candidate using only the supplied job text and persistent context. "
                "Return: score from 0-100, strengths, gaps, deal-breakers, and a recommendation.\n\n"
                + job_text
            )
            result = router.run("rank", prompt)
        else:
            prompt = " ".join(args.prompt).strip() or input("Prompt: ")
            result = router.run(args.task, prompt)

        print(f"[{result.task}] profile={result.profile} model={result.model}")
        print(f"Attempts: {', '.join(result.attempts)}")
        print(result.text)
        return 0
    except (GatewayError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

