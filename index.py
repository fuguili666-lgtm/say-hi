"""Tencent Cloud SCF entrypoint for the daily WeCom greeting."""

from __future__ import annotations

import datetime as dt
import json
import os

from scripts.send_wecom_greeting import SHANGHAI, default_message, send_wecom_text


def main_handler(event, context):
    webhook = os.environ.get("WECOM_WEBHOOK")
    if not webhook:
        raise RuntimeError("Missing WECOM_WEBHOOK environment variable.")

    content = default_message(dt.datetime.now(SHANGHAI))
    result = send_wecom_text(webhook, content, timeout=10.0)

    if result.get("errcode") not in (None, 0):
        raise RuntimeError(f"WeCom returned an error: {json.dumps(result, ensure_ascii=False)}")

    print(json.dumps(result, ensure_ascii=False))
    return result
