#!/usr/bin/env python3
"""Send a Dragon-News Markdown file to Telegram."""

from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import json

REPO = os.getenv("GITHUB_REPOSITORY", "chatdragon75-stack/Dragon-News")
SHA = os.getenv("GITHUB_SHA", "main")


def front_matter(text: str, key: str) -> str:
    match = re.search(rf"^\*\*{re.escape(key)}:\*\*\s*(.*?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)", text, re.MULTILINE)
    if not match:
        return ""
    value = re.sub(r"\s+", " ", match.group(1)).strip()
    return value


def markdown_to_text(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_`>#]", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def github_url(path: str) -> str:
    return f"https://github.com/{REPO}/blob/{SHA}/{quote(path)}"


def build_message(path: str, content: str) -> str:
    title = content.splitlines()[0].lstrip("# ").strip() or Path(path).stem
    date = front_matter(content, "Дата")
    category = front_matter(content, "Категория")
    summary = section(content, "Кратко")
    if not summary:
        summary = markdown_to_text(content)[:1400]

    if path.startswith("daily/"):
        header = "📅 <b>Новая ежедневная сводка Dragon-News</b>"
    else:
        header = "📰 <b>Новая публикация Dragon-News</b>"

    lines = [header, "", f"<b>{html.escape(title)}</b>"]
    if date:
        lines.append(f"📅 {html.escape(date)}")
    if category:
        lines.append(f"🏷 {html.escape(category)}")
    if summary:
        lines.extend(["", html.escape(summary[:1800])])
    lines.extend(["", f'🔗 <a href="{html.escape(github_url(path), quote=True)}">Открыть материал на GitHub</a>'])
    return "\n".join(lines)


def send(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")

    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    topic_id = os.environ.get("TELEGRAM_TOPIC_ID")
    if topic_id:
        payload["message_thread_id"] = int(topic_id)

    request = Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if not result.get("ok"):
        raise SystemExit(f"Telegram API error: {result}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: send_telegram.py <markdown-file>")
    path = sys.argv[1]
    content = Path(path).read_text(encoding="utf-8")
    send(build_message(path, content))


if __name__ == "__main__":
    main()
