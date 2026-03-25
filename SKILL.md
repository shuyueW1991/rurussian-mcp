---
name: rurussian-mcp
description: MCP server for rurussian.com to access Russian language resources and tools.
homepage: https://github.com/shuyueW1991/rurussian-mcp
metadata:
  clawdbot:
    emoji: "🇷🇺"
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
- Buy a RuRussian plan and activate an API key directly from bot flow

Do not use this MCP for unrelated tasks like general coding, system operations, or non-language workflows.

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

- `confirm_key_purchase(session_id, auto_authenticate?, return_api_key?)`
  - Confirms payment completion, gets issued API key, and can auto-authenticate.

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
   - Start payment with `create_key_purchase_session`.
   - Confirm and load key with `confirm_key_purchase`.
   - Or call `authenticate` with an existing key.
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
- If API key errors occur, trigger purchase flow or ask for a valid active RuRussian API key.
- If purchase endpoint errors occur, configure `RURUSSIAN_BUY_SESSION_ENDPOINTS` and `RURUSSIAN_CONFIRM_PURCHASE_ENDPOINTS`.
- If network errors occur, retry and check backend reachability.
