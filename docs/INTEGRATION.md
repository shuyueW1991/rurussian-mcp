# OpenClaw Integration Guide

This guide helps you connect RuRussian MCP to OpenClaw bots and use it as a Russian tutoring backend.

## Prerequisites

- Python 3.9+
- OpenClaw installed and running
- A RuRussian account with an active API key

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
        "RURUSSIAN_API_KEY": "YOUR_RURUSSIAN_API_KEY"
      }
    }
  }
}
```

You can also copy [openclaw_config.json](file:///home/wangshuyue/litelanglearn_repo/mcp-main/rurussian-mcp/examples/openclaw_config.json) as a starting template.

## Step 3: Authenticate in Bot Flow

Before any learning tool call, run:

```json
{
  "name": "authenticate",
  "arguments": {
    "api_key": "YOUR_RURUSSIAN_API_KEY",
    "user_agent": "OpenClaw/1.0"
  }
}
```

Then call tools like `get_word_data`, `get_sentences`, `analyze_sentence`, `generate_zakuska`, and `translate_text`.

## Telegram Setup Flow

- Create a Telegram bot with BotFather.
- Connect your bot token in OpenClaw.
- Ensure your Telegram bot workflow includes an initial `authenticate` call.
- Route learner prompts to RuRussian tools based on intent:
  - Vocabulary lookup → `get_word_data`
  - Grammar breakdown → `analyze_sentence`
  - Practice content → `generate_zakuska`

## Discord Setup Flow

- Create a Discord bot application and invite it to your server.
- Connect it to OpenClaw.
- Add a startup or first-message hook that triggers `authenticate`.
- Route slash commands or messages:
  - `/word <term>` → `get_word_data`
  - `/translate <text>` → `translate_text`
  - `/analyze <sentence>` → `analyze_sentence`

## Advanced Usage

- Set custom user agent:
  - Pass `user_agent` in `authenticate` for analytics segmentation.
- Use a custom API backend:
  - Set `RURUSSIAN_API_URL` when you need an alternate endpoint.
- Build learning routines:
  - Pair `generate_zakuska` output with `analyze_sentence` for guided reading drills.

## Common Issues

- Authentication required
  - You called another tool before `authenticate`.
- Invalid API key
  - Confirm key format and status in your RuRussian account.
- Python runtime mismatch
  - Use Python 3.9 or newer.
- Tool command not available
  - Reinstall in the same environment used by OpenClaw.
