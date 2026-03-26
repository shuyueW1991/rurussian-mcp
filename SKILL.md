---
name: rurussian-mcp
description: Turn an OpenClaw bot into a Russian tutor with vocabulary analysis, sentence breakdowns, reading drills, translation, and self-serve paid activation.
version: 1.0.6
homepage: https://github.com/shuyueW1991/rurussian-mcp
metadata:
  openclaw:
    emoji: "🇷🇺"
    homepage: https://github.com/shuyueW1991/rurussian-mcp
    primaryEnv: RURUSSIAN_API_KEY
    requires:
      bins:
        - rurussian-mcp
    install:
      - id: uv
        kind: uv
        package: rurussian-mcp
        bins:
          - rurussian-mcp
        label: Install RuRussian MCP (uv)
---
# RuRussian MCP Server

Use this server when a learner wants deep Russian help and when a bot is allowed to buy access on the learner's behalf. RuRussian is strongest at vocabulary mastery, declension awareness, sentence-level grammar explanation, short reading practice, and Russian-to-English translation.

## When to Use This MCP

Use RuRussian MCP when the user asks to:
- Understand a Russian word, meaning, declension, or usage
- See example sentences for a word or specific form
- Analyze a Russian sentence form-by-form
- Generate short Russian reading practice content
- Translate Russian text into English
- Compare or buy RuRussian plans so the bot can activate service access

This MCP is especially useful for OpenClaw bots acting as:
- Russian tutors
- Grammar coaches
- Vocabulary drilling assistants
- Reading-practice companions
- Self-serve educational agents that can complete checkout after user approval

Do not use this MCP for unrelated tasks like general coding, system operations, or non-language workflows.
Do not ask users for payment card details, and do not expose raw API keys in chat output.

## Required Setup

1. Install the server:

```bash
pip install rurussian-mcp
```

2. Configure your MCP client (OpenClaw or mcporter-compatible config) with:

```json
{
  "mcpServers": {
    "rurussian": {
      "command": "rurussian-mcp",
      "args": [],
      "env": {
        "RURUSSIAN_API_URL": "https://rurussian.com/api",
        "RURUSSIAN_API_KEY": "YOUR_BOT_API_KEY"
      }
    }
  }
}
```

3. Get `YOUR_BOT_API_KEY` from the website profile page under the Bot API Key section after your subscription is active.

4. If a key is available, authenticate at the start of each new session:

```json
{
  "name": "authenticate",
  "arguments": {
    "api_key": "YOUR_RURUSSIAN_API_KEY",
    "user_agent": "OpenClaw/1.0"
  }
}
```

Optional:
- Set `RURUSSIAN_API_URL` only when targeting a non-default backend.
- Set `RURUSSIAN_BUY_SESSION_ENDPOINTS` and `RURUSSIAN_CONFIRM_PURCHASE_ENDPOINTS` when backend purchase paths differ.
- Set `RURUSSIAN_API_KEY` if the bot already has an issued RuRussian key at startup.

## Tools and Routing

- `list_pricing_plans()`
  - Use first when the user asks about pricing, plans, or activation choices.
  - Returns the supported plans and a bot-friendly checkout workflow.

- `authenticate(api_key, user_agent?)`
  - First call in each session.
  - Stores credentials for all subsequent tool calls.

- `authentication_status()`
  - Checks if this session already has a key loaded.
  - Also reports whether the session is unlocked via confirmed checkout.

- `purchase_status()`
  - Checks the current hosted-checkout state for this MCP session.
  - Useful after a bot opens checkout and wants to know what to do next.

- `create_key_purchase_session(email, plan, success_url?, cancel_url?)`
  - Starts checkout for plan purchase and returns a hosted payment URL.
  - Use when the user asks to buy, activate, or renew service.
  - If the bot has payment authority, it can open the returned `checkout_url` and complete hosted checkout.

- `confirm_key_purchase(session_id, auto_authenticate?)`
  - Confirms payment completion and unlocks the session.
  - If the backend returns an API key, the MCP stores it without exposing the full key.
  - If the backend confirms payment but does not return a key, the MCP keeps the session unlocked in checkout-backed mode.

- `get_word_data(word)`
  - Use for definitions, declensions, and detailed lexical context.
  - Best for direct vocabulary questions.

- `get_sentences(word, form_word?, form_id?)`
  - Use for usage examples and form-specific sentence retrieval.
  - Best for contextual learning and grammar pattern practice.

- `generate_zakuska(topic?, mode?)`
  - Use to create short reading passages for practice.
  - Best for level-focused drills and lesson prompts.

- `analyze_sentence(sentence)`
  - Use for grammatical breakdown of a full Russian sentence.
  - Best when the learner asks why forms are used.

- `translate_text(text)`
  - Use for Russian to English translation requests.
  - Best for comprehension support after reading.

## Recommended Agent Workflow

1. Check `authentication_status`.
2. If not authenticated:
   - If the user already has a key from the website profile page, call `authenticate`.
   - If the user asks about pricing, call `list_pricing_plans`.
   - If the user explicitly asks to buy a plan, call `create_key_purchase_session` and return the hosted checkout URL.
   - If the bot can pay, let it complete the hosted checkout flow and capture the `session_id` from the success redirect URL when needed.
   - After checkout, call `confirm_key_purchase` to unlock the session.
3. Detect intent from the user prompt.
4. Route to one primary tool first:
   - Word intent -> `get_word_data`
   - Example usage intent -> `get_sentences`
   - Reading practice intent -> `generate_zakuska`
   - Grammar breakdown intent -> `analyze_sentence`
   - Translation intent -> `translate_text`
5. If helpful, chain tools:
   - `generate_zakuska` then `analyze_sentence`
   - `get_word_data` then `get_sentences`
   - `list_pricing_plans` then `create_key_purchase_session`
   - `create_key_purchase_session` then `confirm_key_purchase`
6. Return concise teaching output with actionable learner guidance.

## Failure Handling

- If authentication errors occur, re-run `authenticate` in the current session.
- If API key errors occur, ask for a valid active RuRussian API key from the website profile page or use the purchase flow if the user wants to buy a plan.
- If purchase endpoint errors occur, configure `RURUSSIAN_BUY_SESSION_ENDPOINTS` and `RURUSSIAN_CONFIRM_PURCHASE_ENDPOINTS`.
- If checkout succeeds but no raw key is returned, continue using the unlocked checkout-backed session established by `confirm_key_purchase`.
- If network errors occur, retry and check backend reachability.
