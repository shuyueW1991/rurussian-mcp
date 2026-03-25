# OpenClaw Integration Guide

This guide helps you connect RuRussian MCP to OpenClaw bots for Russian tutoring and self-service API key purchase.

## Prerequisites

- Python 3.9+
- OpenClaw installed and running
- A RuRussian account email for checkout

## Step 1: Install the MCP Server

```bash
pip install rurussian-mcp
```

If you run OpenClaw in a virtual environment, install `rurussian-mcp` in that same environment.

## Step 2: Configure OpenClaw

Open your `~/.openclaw/config.json` and add the server entry:

```json
{
  "mcpServers": {
    "rurussian": {
      "command": "rurussian-mcp",
      "args": [],
      "env": {
        "RURUSSIAN_API_URL": "https://rurussian.com/api"
      }
    }
  }
}
```

You can also copy [openclaw_config.json](../examples/openclaw_config.json) as a starting template.

## Step 3: Key Flow in Bot Runtime

- If you already have a key:
  - Call `authenticate(api_key, user_agent?)`.
- If you do not have a key:
  - Call `create_key_purchase_session(email, plan, success_url?, cancel_url?)`.
  - Send `checkout_url` to user and let them finish payment.
  - Call `confirm_key_purchase(session_id)` to fetch and load the new key.

## Step 4: Learning Tools

After authentication, call tools like `get_word_data`, `get_sentences`, `analyze_sentence`, `generate_zakuska`, and `translate_text`.

## Telegram Setup Flow

- Create a Telegram bot with BotFather.
- Connect your bot token in OpenClaw.
- Add startup logic:
  - Check `authentication_status`.
  - If not authenticated, trigger purchase flow or prompt for existing key.
- Route learner prompts to RuRussian tools based on intent:
  - Vocabulary lookup → `get_word_data`
  - Grammar breakdown → `analyze_sentence`
  - Practice content → `generate_zakuska`

## Discord Setup Flow

- Create a Discord bot application and invite it to your server.
- Connect it to OpenClaw.
- Add first-message hook:
  - Check `authentication_status`.
  - If not authenticated, use purchase flow.
- Route slash commands or messages:
  - `/word <term>` → `get_word_data`
  - `/translate <text>` → `translate_text`
  - `/analyze <sentence>` → `analyze_sentence`

## Advanced Usage

- Set custom user agent:
  - Pass `user_agent` in `authenticate` for analytics segmentation.
- Use a custom API backend:
  - Set `RURUSSIAN_API_URL` when you need an alternate endpoint.
- Override purchase endpoint paths:
  - Set `RURUSSIAN_BUY_SESSION_ENDPOINTS`.
  - Set `RURUSSIAN_CONFIRM_PURCHASE_ENDPOINTS`.

## Common Issues

- Authentication required
  - You called another tool before key setup.
- Purchase endpoint not found
  - Configure `RURUSSIAN_BUY_SESSION_ENDPOINTS` and `RURUSSIAN_CONFIRM_PURCHASE_ENDPOINTS`.
- Invalid API key
  - Re-run `confirm_key_purchase` after payment or use a valid key in `authenticate`.
- Python runtime mismatch
  - Use Python 3.9 or newer.
- Tool command not available
  - Reinstall in the same environment used by OpenClaw.
