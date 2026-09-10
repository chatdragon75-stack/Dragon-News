# 🐉 Telegram Bot Integration

Telegram Bot Integration for **Dragon-News**. The integration provides a news bot foundation, automatic GitHub → Telegram publishing, GitHub notifications, dragon content, and future **Lumendra** AI mode.

## Architecture

```text
Telegram
   ↑
GitHub Actions ──→ Dragon-News
   ↑
Bot handlers
   ├── News
   ├── Daily digest
   ├── GitHub updates
   ├── Dragon encyclopedia
   └── Lumendra AI
```

## Local setup

1. Create a bot with `@BotFather` and copy the token.
2. Copy `.env.example` to `.env`.
3. Put the token into `TELEGRAM_BOT_TOKEN`.
4. Set `TELEGRAM_CHAT_ID` to the destination chat/group/channel ID.
5. Optionally set `TELEGRAM_TOPIC_ID` for a forum topic.
6. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

7. Start the bot:

```bash
python examples/python/basic_bot.py
```

## GitHub Actions → Telegram

The workflow `.github/workflows/telegram-news.yml` automatically publishes new or modified Markdown materials from `news/` and `daily/` to Telegram when they are committed to `main`.

### Required GitHub Actions secrets

- `TELEGRAM_BOT_TOKEN` — token from `@BotFather`.
- `TELEGRAM_CHAT_ID` — destination chat/group/channel ID.

Optional:

- `TELEGRAM_TOPIC_ID` — forum topic/thread ID.

The token is read only from GitHub Actions Secrets and is never stored in the repository.

### Manual test

Open **Actions → 🐉 Dragon-News → Telegram → Run workflow**. A manual run publishes the newest available article/daily digest.

## Commands

- `/start`
- `/help`
- `/news`
- `/daily`
- `/dragons`
- `/art`
- `/github`
- `/lumendra`

`/news` and `/daily` are connected to the Dragon-News repository. The dragon, art, GitHub, and Lumendra handlers are currently starter placeholders and will be connected in the next integration stages.

## Production

Use long polling during development. For production, prefer a webhook with HTTPS and Telegram's webhook secret token. Telegram documents `getUpdates` and webhooks as mutually exclusive update-delivery mechanisms.

## Security

Never commit `.env` or a real bot token. If a token is exposed, revoke/rotate it through BotFather immediately.

## Roadmap

- [x] Base skill documentation
- [x] Python starter bot
- [x] Environment template
- [x] Dragon-News repository parser
- [x] GitHub Actions → Telegram publishing
- [ ] Daily digest scheduler
- [ ] GitHub event notifications
- [ ] Dragon encyclopedia commands
- [ ] Dragon-Art-Project gallery commands
- [ ] Lumendra AI provider interface
- [ ] Production webhook deployment
