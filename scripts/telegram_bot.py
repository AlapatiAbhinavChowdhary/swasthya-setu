"""Environment-gated Telegram adapter with deterministic dry-run behavior."""

from __future__ import annotations

import os


def handle_message(message: str) -> str:
    from swasthya_setu.generation.agent import run_agent

    return run_agent(message, session_id="telegram-dry-run")["answer"]


def main() -> None:
    if os.getenv("TELEGRAM_DRY_RUN", "").lower() in {"1", "true", "yes"}:
        print(handle_message(os.getenv("TELEGRAM_TEST_MESSAGE", "What is dengue?")))
        return
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        raise SystemExit("Set TELEGRAM_BOT_TOKEN or TELEGRAM_DRY_RUN=true.")
    raise SystemExit(
        "Live Telegram polling is intentionally disabled until a deployment account is configured."
    )


if __name__ == "__main__":
    main()
