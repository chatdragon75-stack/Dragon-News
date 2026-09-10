"""Read Dragon-News Markdown content for the Telegram bot."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

import requests


CATEGORIES = {
    "dragons-fantasy": "🐉 Драконы, фэнтези и книги",
    "art": "🎨 Арт, иллюстрации и художники",
    "ai-tech": "🤖 ИИ и технологии",
    "programming-github": "💻 Программирование и GitHub",
    "games": "🎮 Игры",
    "gadgets-apps": "📱 Приложения и гаджеты",
    "world": "🌍 Мировые новости",
}


@dataclass(frozen=True)
class NewsItem:
    title: str
    date: str
    category: str
    summary: str
    url: str
    content: str = ""


class DragonNewsRepository:
    """Small read-only client for the public Dragon-News GitHub repository."""

    def __init__(self, repository: str, branch: str = "main", timeout: int = 10) -> None:
        self.repository = repository
        self.branch = branch
        self.timeout = timeout
        self.api_base = f"https://api.github.com/repos/{repository}"

    def _get_json(self, path: str):
        response = requests.get(f"{self.api_base}/contents/{path}", params={"ref": self.branch}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _get_text(self, path: str) -> str:
        response = requests.get(
            f"https://raw.githubusercontent.com/{self.repository}/{self.branch}/{path}",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.text

    @staticmethod
    def _front_matter(content: str, key: str) -> str:
        match = re.search(rf"^\*\*{re.escape(key)}:\*\*\s*(.*?)\s*$", content, re.MULTILINE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _section(content: str, heading: str) -> str:
        match = re.search(rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)", content, re.MULTILINE)
        return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""

    def latest_daily(self) -> tuple[str, str] | None:
        years = self._get_json("daily")
        year_dirs = sorted((item["name"] for item in years if item.get("type") == "dir"), reverse=True)
        for year in year_dirs:
            files = self._get_json(f"daily/{year}")
            candidates = sorted(
                (item["name"] for item in files if item.get("type") == "file" and item["name"].endswith(".md")),
                reverse=True,
            )
            if candidates:
                path = f"daily/{year}/{candidates[0]}"
                return path, self._get_text(path)
        return None

    def latest_articles(self, limit: int = 5, category: str | None = None) -> list[NewsItem]:
        entries = self._get_json("news")
        items: list[NewsItem] = []
        for entry in entries:
            if entry.get("type") != "file" or not entry.get("name", "").endswith(".md"):
                continue
            if entry["name"] in {"README.md", "ARTICLE-TEMPLATE.md"}:
                continue
            content = self._get_text(entry["path"])
            raw_date = self._front_matter(content, "Дата")
            try:
                date.fromisoformat(raw_date)
            except ValueError:
                continue
            item_category = self._front_matter(content, "Категория")
            if category and item_category != category and CATEGORIES.get(category) != item_category:
                continue
            items.append(NewsItem(
                title=content.splitlines()[0].lstrip("# ").strip(),
                date=raw_date,
                category=item_category,
                summary=self._section(content, "Кратко"),
                url=entry.get("html_url", ""),
                content=content,
            ))
        items.sort(key=lambda item: item.date, reverse=True)
        return items[:limit]

    def categories(self) -> dict[str, str]:
        return dict(CATEGORIES)

    def format_article(self, item: NewsItem, max_chars: int = 3500) -> str:
        details = self._section(item.content, "Подробности") or item.summary
        context = self._section(item.content, "Контекст")
        parts = [f"📰 <b>{item.title}</b>", f"📅 {item.date}"]
        if item.category:
            parts.append(f"🏷 {item.category}")
        if item.summary:
            parts.append(f"\n<b>Кратко</b>\n{item.summary}")
        if details:
            parts.append(f"\n<b>Подробности</b>\n{details}")
        if context:
            parts.append(f"\n<b>Контекст</b>\n{context}")
        return "\n".join(parts)[:max_chars]

    def format_latest_daily(self, max_chars: int = 3800) -> str:
        latest = self.latest_daily()
        if not latest:
            return "Пока нет опубликованных ежедневных сводок."
        path, content = latest
        title = content.splitlines()[0].lstrip("# ").strip() or path.rsplit("/", 1)[-1]
        body = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", content)
        body = re.sub(r"^#{1,6}\s*", "", body, flags=re.MULTILINE)
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        return f"📅 <b>{title}</b>\n\n{body[:max_chars]}"
