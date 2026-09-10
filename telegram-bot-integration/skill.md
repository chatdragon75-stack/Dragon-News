# Telegram Bot Integration Skill v1.0

## Purpose

This skill defines a reusable workflow for designing, implementing, configuring, testing, and deploying Telegram bots. It is optimized for the Dragon-News project and can later power a Dragon World / Lumendra bot.

## Core capabilities

- Create and configure Telegram bots through BotFather.
- Use the Telegram Bot API over HTTPS.
- Receive updates with long polling (`getUpdates`) or webhooks (`setWebhook`).
- Implement commands, text handlers, callback queries, inline keyboards, media, and documents.
- Publish Dragon-News items and daily digests.
- Connect Telegram notifications to GitHub project activity.
- Prepare an AI assistant mode for Lumendra.
- Keep bot tokens and secrets outside source control.
- Add logging, error handling, health checks, and deployment configuration.

## Default stack

- Python 3.12+
- `python-telegram-bot` 22.x
- Environment variables via `.env` for local development.
- Long polling for local development.
- Webhooks for production deployments where a stable HTTPS endpoint is available.

## Security rules

1. Never place `TELEGRAM_BOT_TOKEN` directly in source code.
2. Never commit `.env` files containing real credentials.
3. Use `.env.example` with placeholders only.
4. Rotate a token immediately if it is exposed.
5. Validate webhook requests and use Telegram's `secret_token` when webhooks are used.
6. Restrict administrative commands to an explicit allowlist of Telegram user/chat IDs.
7. Do not log bot tokens or sensitive user data.

## Recommended Dragon-News commands

- `/start` — welcome message.
- `/help` — command list.
- `/news` — latest news.
- `/daily` — latest daily digest.
- `/dragons` — dragon encyclopedia entry or menu.
- `/art` — latest dragon art.
- `/github` — recent project updates.
- `/lumendra` — start a conversation with Lumendra mode.

## Interaction pattern

Prefer clear menus with inline buttons. Callback data should be short, stable, and validated server-side. Long-running work should not block the Telegram update handler.

## Dragon-News integration

The bot should treat Dragon-News as a content source rather than duplicating the entire archive. A future implementation can read structured files from the repository, select the newest validated entries, and format them for Telegram.

Suggested flow:

`news file -> parser -> formatter -> Telegram message -> optional inline buttons`

## AI / Lumendra integration

The future AI mode should be isolated behind a provider interface so the Telegram layer does not depend on one AI vendor. The bot receives a message, passes sanitized conversation context to the provider, and sends the generated answer back to Telegram.

## Error handling

- Catch Telegram API/network errors.
- Retry transient failures with bounded backoff.
- Avoid infinite retry loops.
- Log actionable diagnostics without secrets.
- Return a friendly fallback message to users when an operation fails.

## Deployment phases

### Phase 1 — local

Use long polling and `.env`.

### Phase 2 — server

Run the bot as a managed service/container and use environment-based secrets.

### Phase 3 — webhook

Expose a stable HTTPS endpoint, configure `setWebhook`, use a secret token, and monitor webhook health.

### Phase 4 — project automation

Connect GitHub/Dragon-News updates and scheduled daily digests.

### Phase 5 — Lumendra

Add the AI conversation layer, memory policy, lore retrieval, and dragon-world commands.

## Implementation standard

Use asynchronous handlers with `python-telegram-bot`. Keep Telegram-specific code separate from news parsing, GitHub integration, and AI provider code.

## Done criteria for v1

A minimal implementation is complete when:

- the bot starts from an environment variable;
- `/start` and `/help` work;
- `/news` returns a placeholder/latest news response;
- inline buttons work;
- errors are handled;
- no secret is committed;
- the README explains setup and execution.
