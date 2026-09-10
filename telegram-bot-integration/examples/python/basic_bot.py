"""Minimal Dragon-News Telegram bot starter."""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    return token


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("📰 Новости", callback_data="news"),
            InlineKeyboardButton("🐉 Драконы", callback_data="dragons"),
        ],
        [InlineKeyboardButton("✨ Люмендра", callback_data="lumendra")],
    ]
    await update.effective_message.reply_text(
        "🐉 Добро пожаловать в Dragon-News!\n\n"
        "Я буду присылать новости, арты, материалы о драконах "
        "и обновления проектов.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "Доступные команды:\n"
        "/start — главное меню\n"
        "/help — помощь\n"
        "/news — последние новости\n"
        "/daily — ежедневная сводка\n"
        "/dragons — энциклопедия драконов\n"
        "/art — последние арты\n"
        "/github — обновления GitHub\n"
        "/lumendra — режим Люмендры"
    )


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "📰 Dragon-News\n\n"
        "Модуль чтения новостей будет подключён следующим этапом."
    )


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "📚 Ежедневная сводка пока готовится.\n"
        "Следующий этап — подключить архив daily/."
    )


async def dragons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "🐲 Энциклопедия драконов скоро будет подключена."
    )


async def art(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "🎨 Галерея Dragon-Art-Project будет подключена следующим этапом."
    )


async def github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "💻 GitHub-интеграция будет показывать обновления Dragon-News "
        "и Dragon-Art-Project."
    )


async def lumendra(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "✨ Я — Люмендра, дракон знаний и историй.\n\n"
        "AI-провайдер будет подключён отдельным модулем, "
        "чтобы Telegram-слой оставался независимым."
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    handlers = {
        "news": news,
        "dragons": dragons,
        "lumendra": lumendra,
    }
    handler = handlers.get(query.data)
    if handler:
        await handler(update, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled Telegram error", exc_info=context.error)


 def main() -> None:
    application = Application.builder().token(get_token()).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("dragons", dragons))
    application.add_handler(CommandHandler("art", art))
    application.add_handler(CommandHandler("github", github))
    application.add_handler(CommandHandler("lumendra", lumendra))
    application.add_handler(CallbackQueryHandler(button))
    application.add_error_handler(error_handler)

    logger.info("Dragon-News Telegram bot is starting")
    application.run_polling()


if __name__ == "__main__":
    main()
