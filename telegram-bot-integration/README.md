# 🐉 Telegram Bot Integration

Telegram Bot Integration for **Dragon-News**. The first release provides a clean foundation for a news bot, GitHub notifications, dragon content, and future **Lumendra** AI mode.

## Architecture

```text
Telegram
   ↓
Bot handlers
   ├── Dragon-News
   ├── GitHub updates
   ├── Dragon encyclopedia
   └── Lumendra AI
```

## Local setup

1. Create a bot with `@BotFather` and copy the token.
2. Copy `.env.example` to `.env`.
3. Put the token into `TELEGRAM_BOT_TOKEN`.
4. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

5. Start the bot:

```bash
python examples/python/basic_bot.py
```

## Commands

- `/start`
- `/help`
- `/news`
- `/daily`
- `/dragons`
- `/art`
- `/github`
- `/lumendra`

The current starter bot keeps `/news` as a safe placeholder until the repository's structured news parser is connected.

## Production

Use long polling during development. For production, prefer a webhook with HTTPS and Telegram's webhook secret token. Telegram documents `getUpdates` and webhooks as mutually exclusive update-delivery mechanisms.

## Security

Never commit `.env` or a real bot token. If a token is exposed, revoke/rotate it through BotFather immediately.

## Roadmap

- [x] Base skill documentation
- [x] Python starter bot
- [x] Environment template
- [ ] Dragon-News parser
- [ ] Daily digest scheduler
- [ ] GitHub event notifications
- [ ] Dragon encyclopedia commands
- [ ] Lumendra AI provider interface
- [ ] Production webhook deployment
