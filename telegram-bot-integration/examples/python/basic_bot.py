"""Minimal Dragon-News Telegram bot with live repository news."""

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

from src.news_repository import DragonNewsRepository  # noqa: E402

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("📰 Новости", callback_data="news"), InlineKeyboardButton("🐉 Драконы", callback_data="dragons")],
        [InlineKeyboardButton("📅 Сводка", callback_data="daily"), InlineKeyboardButton("✨ Люмендра", callback_data="lumendra")],
    ]
    await update.effective_message.reply_text(
        "🐉 Добро пожаловать в Dragon-News!\n\n"
        "Новости теперь читаются прямо из репозитория.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Доступные команды:\n"
        "/start — главное меню\n/help — помощь\n/news — последние новости\n"
        "/daily — ежедневная сводка\n/dragons — энциклопедия драконов\n"
        "/art — последние арты\n/github — обновления GitHub\n/lumendra — режим Люмендры"
    )


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        items = repository().latest_articles(limit=5)
    except Exception:
        logger.exception("Failed to read Dragon-News articles")
        await update.effective_message.reply_text("📰 Не удалось прочитать архив новостей. Попробуйте позже.")
        return

    if not items:
        await update.effective_message.reply_text(
            "📰 Архив новостей пока пуст.\n\n"
            "Добавьте статьи Markdown в news/ по шаблону ARTICLE-TEMPLATE.md."
        )
        return

    lines = ["📰 <b>Последние новости Dragon-News</b>"]
    for item in items:
        title = html.escape(item.title)
        category = f" · {html.escape(item.category)}" if item.category else ""
        summary = f"\n{html.escape(item.summary)}" if item.summary else ""
        lines.append(f"\n<b>{title}</b>\n📅 {html.escape(item.date)}{category}{summary}")
    await update.effective_message.reply_text("\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = repository().format_latest_daily()
    except Exception:
        logger.exception("Failed to read daily digest")
        text = "📅 Не удалось прочитать ежедневную сводку. Попробуйте позже."
    await update.effective_message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)


async def dragons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("🐲 Энциклопедия драконов скоро будет подключена.")


async def art(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("🎨 Галерея Dragon-Art-Project скоро будет подключена.")


async def github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("💻 GitHub-интеграция будет показывать обновления Dragon-News и Dragon-Art-Project.")


async def lumendra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "✨ Я — Люмендра, дракон знаний и историй.\n\n"
        "AI-провайдер будет подключён отдельным модулем."
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    handlers = {"news": news, "daily": daily, "dragons": dragons, "lumendra": lumendra}
    handler = handlers.get(query.data)
    if handler:
        await handler(update, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled Telegram error", exc_info=context.error)


def main() -> None:
    application = Application.builder().token(get_token()).build()
    for command, handler in {
        "start": start, "help": help_command, "news": news, "daily": daily,
        "dragons": dragons, "art": art, "github": github, "lumendra": lumendra,
    }.items():
        application.add_handler(CommandHandler(command, handler))
    application.add_handler(CallbackQueryHandler(button))
    application.add_error_handler(error_handler)
    logger.info("Dragon-News Telegram bot is starting")
    application.run_polling()


if __name__ == "__main__":
    main()
