"""Dragon-News Telegram bot example."""

from __future__ import annotations

import html
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.news_repository import CATEGORIES, DragonNewsRepository  # noqa: E402

load_dotenv()
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def get_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    return token


def repository() -> DragonNewsRepository:
    return DragonNewsRepository(os.getenv("DRAGON_NEWS_REPOSITORY", "chatdragon75-stack/Dragon-News"))


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📰 Новости", callback_data="news"), InlineKeyboardButton("📅 Сводка", callback_data="daily")],
        [InlineKeyboardButton("🐉 Драконы", callback_data="dragons"), InlineKeyboardButton("🎨 Арт", callback_data="art")],
        [InlineKeyboardButton("💻 GitHub", callback_data="github"), InlineKeyboardButton("✨ Люмендра", callback_data="lumendra")],
    ])


def category_menu() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(label, callback_data=f"cat:{key}")] for key, label in CATEGORIES.items()]
    rows.append([InlineKeyboardButton("⬅️ Главное меню", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("🐉 <b>Dragon-News</b>\n\nВыберите раздел:", reply_markup=main_menu(), parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "<b>Команды Dragon-News</b>\n\n/start — главное меню\n/help — помощь\n/news — новости и категории\n"
        "/daily — последняя сводка\n/dragons — энциклопедии\n/art — Dragon-Art-Project\n/github — обновления GitHub\n/lumendra — режим Люмендры",
        parse_mode="HTML",
    )


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("📰 <b>Категории новостей</b>\n\nВыберите тему:", reply_markup=category_menu(), parse_mode="HTML")


async def category(update: Update, category_key: str) -> None:
    if category_key not in CATEGORIES:
        await update.effective_message.reply_text("Неизвестная категория.")
        return
    try:
        items = repository().latest_articles(limit=5, category=category_key)
    except Exception:
        logger.exception("Failed to read news category")
        await update.effective_message.reply_text("📰 Не удалось прочитать эту категорию. Попробуйте позже.")
        return
    label = CATEGORIES[category_key]
    if not items:
        await update.effective_message.reply_text(f"{label}\n\nПока здесь нет опубликованных материалов.", reply_markup=category_menu())
        return
    rows = [[InlineKeyboardButton(f"{item.date} — {item.title[:45]}", callback_data=f"article:{index}:{category_key}")] for index, item in enumerate(items)]
    rows.append([InlineKeyboardButton("⬅️ Категории", callback_data="news")])
    await update.effective_message.reply_text(f"{label}\n\nПоследние материалы:", reply_markup=InlineKeyboardMarkup(rows))


async def show_article(update: Update, index: int, category_key: str) -> None:
    try:
        items = repository().latest_articles(limit=10, category=category_key)
        item = items[index]
    except (IndexError, ValueError):
        await update.effective_message.reply_text("📰 Новость больше недоступна. Откройте /news ещё раз.")
        return
    except Exception:
        logger.exception("Failed to read article")
        await update.effective_message.reply_text("📰 Не удалось открыть новость. Попробуйте позже.")
        return
    text = html.escape(repository().format_article(item), quote=False)
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    keyboard = [[InlineKeyboardButton("🔗 Открыть источник", url=item.url)], [InlineKeyboardButton("⬅️ Назад", callback_data=f"cat:{category_key}")]]
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = repository().format_latest_daily()
    except Exception:
        logger.exception("Failed to read daily digest")
        text = "📅 Не удалось прочитать ежедневную сводку. Попробуйте позже."
    await update.effective_message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)


async def dragons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo = os.getenv("DRAGON_ART_REPOSITORY", "chatdragon75-stack/Dragon-Art-Project")
    await update.effective_message.reply_text("🐲 <b>Энциклопедии драконов</b>\n\nInheritance Cycle, Temeraire, The Dragon Prince, Dragon Adventures и Ninjago.\n\n" + f"https://github.com/{repo}/tree/main/encyclopedias", parse_mode="HTML", disable_web_page_preview=True)


async def art(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo = os.getenv("DRAGON_ART_REPOSITORY", "chatdragon75-stack/Dragon-Art-Project")
    await update.effective_message.reply_text("🎨 <b>Dragon-Art-Project</b>\n\n" + f"https://github.com/{repo}/tree/main/art", parse_mode="HTML", disable_web_page_preview=True)


async def github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo = os.getenv("DRAGON_NEWS_REPOSITORY", "chatdragon75-stack/Dragon-News")
    try:
        import requests
        response = requests.get(f"https://api.github.com/repos/{repo}/commits", params={"per_page": 5}, timeout=10)
        response.raise_for_status()
        lines = ["💻 <b>Последние обновления GitHub</b>"]
        for commit in response.json():
            message = html.escape(commit["commit"]["message"].splitlines()[0])
            url = html.escape(commit.get("html_url", ""), quote=True)
            lines.append(f"\n• <b>{message}</b>\n<a href=\"{url}\">Открыть commit</a>")
        await update.effective_message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        logger.exception("Failed to read GitHub commits")
        await update.effective_message.reply_text("💻 Не удалось получить обновления GitHub. Попробуйте позже.")


async def lumendra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("✨ <b>Люмендра</b>\n\nЯ — дракон знаний и историй.\n\nСледующий слой — AI-провайдер и база лора нашего мира.", parse_mode="HTML")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if data == "menu":
        await query.message.reply_text("🐉 <b>Главное меню</b>", reply_markup=main_menu(), parse_mode="HTML")
    elif data == "news":
        await news(update, context)
    elif data == "daily":
        await daily(update, context)
    elif data == "dragons":
        await dragons(update, context)
    elif data == "art":
        await art(update, context)
    elif data == "github":
        await github(update, context)
    elif data == "lumendra":
        await lumendra(update, context)
    elif data.startswith("cat:"):
        await category(update, data.split(":", 1)[1])
    elif data.startswith("article:"):
        _, index, category_key = data.split(":", 2)
        await show_article(update, int(index), category_key)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled Telegram error", exc_info=context.error)


def main() -> None:
    application = Application.builder().token(get_token()).build()
    for command, handler in {"start": start, "help": help_command, "news": news, "daily": daily, "dragons": dragons, "art": art, "github": github, "lumendra": lumendra}.items():
        application.add_handler(CommandHandler(command, handler))
    application.add_handler(CallbackQueryHandler(button))
    application.add_error_handler(error_handler)
    logger.info("Dragon-News Telegram bot is starting")
    application.run_polling()


if __name__ == "__main__":
    main()
