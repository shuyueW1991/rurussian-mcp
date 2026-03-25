# RuRussian MCP Server

[![Works with OpenClaw](https://img.shields.io/badge/Works%20with-OpenClaw-4f46e5)](https://openclaw.dev)
[![MCP Server](https://img.shields.io/badge/MCP-Server-0891b2)](https://modelcontextprotocol.io)
[![Russian Learning](https://img.shields.io/badge/Russian-Learning-16a34a)](https://rurussian.com)

MCP server for RURussian.com – turn your OpenClaw bot into a Russian tutor.
Rurussian.com is a state-of-the-art tool designed for deep, immersive mastery of Russian vocabulary. At its core, it features sentence-driven declension memorization to help you internalize grammar naturally in context, plus precise, native-level text generation for individual words and full sentences. All generated content is laser-focused on the real-world, typical usage of terms as they appear in formal dictionary definitions. What’s more, the platform lets you create fully customized textbooks aligned exactly with your learning level and progress, with GPT-5-powered AI delivering in-depth, granular analysis of every sentence you collect and study.
Rurussian.com is built to sustain a long-term Russian learning journey.




## Quick Start

1. Install the server:

```bash
pip install rurussian-mcp
```

2. Add this to your `~/.openclaw/config.json`:

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

3. If the bot already has a key, call `authenticate` first.
4. If the bot has no key yet and the user wants to buy one, run `create_key_purchase_session`, let the user complete hosted checkout, then run `confirm_key_purchase`.
5. `confirm_key_purchase` can auto-authenticate the session, but it never returns a raw API key.

For a drop-in example file, see [openclaw_config.json](./examples/openclaw_config.json).

## Tool List

- `authenticate(api_key, user_agent?)`
  - Example request: "Use my RuRussian API key and initialize this session."
- `authentication_status()`
  - Example request: "Check whether this session is already authenticated."
- `create_key_purchase_session(email, plan, success_url?, cancel_url?)`
  - Example request: "Create a checkout session for `month_1` and return the payment URL."
- `confirm_key_purchase(session_id, auto_authenticate?)`
  - Example request: "Confirm the payment session and auto-authenticate if a key is issued."
- `get_word_data(word)`
  - Example request: "Explain the declension and meaning of `книга`."
- `get_sentences(word, form_word?, form_id?)`
  - Example request: "Show example sentences for `идти` in past tense."
- `generate_zakuska(topic?, mode?)`
  - Example request: "Generate a short A2-level Russian text about travel."
- `analyze_sentence(sentence)`
  - Example request: "Break down this sentence and explain each form: `Я люблю программировать`."
- `translate_text(text)`
  - Example request: "Translate this Russian paragraph to English."

## Full Docs and API Access

- Website: [rurussian.com](https://rurussian.com)
- Full documentation and integration details: [rurussian.com](https://rurussian.com)
- Pricing plans: [rurussian.com/pricing](https://rurussian.com/pricing)
- API key signup and account dashboard: [rurussian.com](https://rurussian.com)

## Troubleshooting

- Missing API key
  - Pass a valid key into `authenticate`, or use the purchase flow if the user wants to buy a plan.
- Authentication required error
  - Call `authenticate` before any other MCP tool in each new server session.
- Purchase endpoint mismatch
  - Set `RURUSSIAN_BUY_SESSION_ENDPOINTS` and `RURUSSIAN_CONFIRM_PURCHASE_ENDPOINTS` when your backend paths differ.
- Python version issue
  - This package requires Python 3.9 or newer.
- Command not found: `rurussian-mcp`
  - Ensure installation completed in the same environment where OpenClaw runs.
- API endpoint/network errors
  - Verify internet access and optionally set `RURUSSIAN_API_URL` only if you need a custom backend URL.

## Security Notes

- This repo contains no built-in secrets and no real keys.
- Purchase helpers can initiate hosted checkout and confirm a session, but payment is still completed on the RuRussian checkout page rather than inside the tool.
- The server never returns a full API key in tool output.
- Do not commit real keys to config files. Use environment variables in deployment platforms.

## Integration Guide

For extended OpenClaw integration steps and platform setup ideas, see [INTEGRATION.md](./docs/INTEGRATION.md).

## License

MIT. See [LICENSE](./LICENSE).
