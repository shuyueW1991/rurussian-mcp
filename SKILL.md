---
name: rurussian-mcp
description: MCP server for rurussian.com to access Russian language resources and tools.
version: 1.0.3
homepage: https://github.com/shuyueW1991/rurussian-mcp
metadata: { "openclaw": { "emoji": "🇷🇺", "homepage": "https://github.com/shuyueW1991/rurussian-mcp", "requires": { "bins": ["rurussian-mcp"] }, "install": [{ "id": "uv", "kind": "uv", "package": "rurussian-mcp", "bins": ["rurussian-mcp"], "label": "Install RuRussian MCP (uv)" }] } }
---
# RuRussian MCP Server

Use this server when a learner asks for Russian vocabulary help, grammar analysis, sentence examples, short practice texts, or translation.

## When to Use This MCP

Use RuRussian MCP when the user asks to:
- Understand a Russian word, meaning, declension, or usage
- See example sentences for a word or specific form
- Analyze a Russian sentence form-by-form
- Generate short Russian reading practice content
- Translate Russian text into English

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
        "RURUSSIAN_API_URL": "https://rurussian.com/api"
      }
    }
  }
}
```

3. If a key is available, authenticate at the start of each new session:

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

## Tools and Routing

- `authenticate(api_key, user_agent?)`
  - First call in each session.
  - Stores credentials for all subsequent tool calls.

- `authentication_status()`
  - Checks if this session already has a key loaded.

- `create_key_purchase_session(email, plan, success_url?, cancel_url?)`
  - Starts checkout for plan purchase and returns a hosted payment URL.
  - Only use when the user explicitly asks to buy or activate a plan.

- `confirm_key_purchase(session_id, auto_authenticate?)`
  - Confirms payment completion and can auto-authenticate, but never returns a raw API key.

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
   - If the user already has a key, call `authenticate`.
   - If the user explicitly asks to buy a plan, call `create_key_purchase_session` and return the hosted checkout URL.
   - After the user completes checkout, call `confirm_key_purchase` to auto-authenticate the session.
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
6. Return concise teaching output with actionable learner guidance.

## Failure Handling

- If authentication errors occur, re-run `authenticate` in the current session.
- If API key errors occur, ask for a valid active RuRussian API key from the official account dashboard or use the purchase flow if the user wants to buy a plan.
- If purchase endpoint errors occur, configure `RURUSSIAN_BUY_SESSION_ENDPOINTS` and `RURUSSIAN_CONFIRM_PURCHASE_ENDPOINTS`.
- If network errors occur, retry and check backend reachability.
