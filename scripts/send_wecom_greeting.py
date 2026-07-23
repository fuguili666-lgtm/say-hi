#!/usr/bin/env python3
"""Send a daily greeting to an Enterprise WeChat robot webhook."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
SHANGHAI = ZoneInfo("Asia/Shanghai")


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def default_message(now: dt.datetime) -> str:
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekday_names[now.weekday()]
    return f"早上好，今天是 {now:%Y-%m-%d} {weekday}。世间万事，骤雨不终日，飘风不终朝。via github"


def send_wecom_text(webhook: str, content: str, timeout: float) -> dict[str, object]:
    payload = {
        "msgtype": "text",
        "text": {
            "content": content,
        },
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        webhook,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"raw": body}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", help="Greeting content. Defaults to a date-aware greeting.")
    parser.add_argument("--webhook", help="Enterprise WeChat webhook URL. Overrides WECOM_WEBHOOK.")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Print the payload without sending it.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    load_dotenv(ENV_FILE)
    args = parse_args(argv)

    content = args.message or default_message(dt.datetime.now(SHANGHAI))
    webhook = args.webhook or os.environ.get("WECOM_WEBHOOK")

    payload = {"msgtype": "text", "text": {"content": content}}
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not webhook:
        print("Missing WECOM_WEBHOOK. Set it in the environment or in .env.", file=sys.stderr)
        return 2

    try:
        result = send_wecom_text(webhook, content, args.timeout)
    except urllib.error.URLError as exc:
        print(f"Failed to send greeting: {exc}", file=sys.stderr)
        return 1

    if result.get("errcode") not in (None, 0):
        print(f"WeCom returned an error: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
