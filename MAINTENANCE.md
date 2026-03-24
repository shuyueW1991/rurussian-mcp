# Maintenance Document for RuRussian MCP Server

## Overview
This document outlines the maintenance responsibilities for the `rurussian-mcp` package. 

To guarantee the highest level of security, the MCP server does **not** contain any database connections, OpenAI keys, or proprietary backend logic. Instead, it operates as a lightweight HTTP client that routes MCP tool calls directly to the `rurussian.com` Next.js backend (`/api/*`).

## 1. Backend API Sync (Crucial)
The MCP server relies on your Next.js API endpoints.

**Maintenance Action:**
- If you change the API routes in your main `rurussian.com` frontend (e.g., modifying `app/api/[...slug]/route.ts`), you must ensure the routes used by this MCP server (in `rurussian_mcp/server.py`) remain compatible.
- The endpoints currently used are:
  - `GET /api/word/[word]`
  - `GET /api/rusvibe/sentences`
  - `POST /api/zakuska/generate`
  - `POST /api/analyze_sentence`
  - `POST /api/translate`

## 2. API Key Authentication (Next.js Side)
The MCP server accepts an API key from the user via the `authenticate` tool and passes it to your backend as an `Authorization: Bearer <API_KEY>` header.

**Maintenance Action:**
- **Implement API Key Validation in Next.js:** Update your `app/api/[...slug]/route.ts` to check for the `Authorization` header.
- **Enforce Stripe Plans:** In your backend API logic, when verifying the API key, ensure that the user account associated with the key has an `active` bot/Stripe subscription.
- **Log Usage:** In your Next.js route, after successfully validating the key, log the endpoint access and `User-Agent` to the `mcp_usage_logs` table (added to your `rds_storage.py` previously).

## 3. Database Schema
You have extended your core `rds_storage.py` with tables for MCP tracking:
- `bot_api_keys`: Maps `user_email` to their generated API key (`api_key`).
- `mcp_usage_logs`: Logs every successful tool call by a bot (including `user_agent` and `endpoint` used) for monitoring and auditing.

**Maintenance Action:** 
- Monitor `mcp_usage_logs` size. You may need to set up a cron job to archive or clean up old logs to prevent RDS bloat.
- Provide a UI on `rurussian.com` for users to generate and manage their API keys.

## 4. Publishing to PyPI
To distribute updates to the bots:

1. Update the `version` in `pyproject.toml`.
2. Build the package: `python -m build`
3. Upload to PyPI: `twine upload dist/*`

**Maintenance Action:**
- Keep your PyPI credentials secure.
- Consider automating the PyPI release via GitHub Actions whenever a new release tag is created.

## 5. Docker Image Updates
Users who prefer containerization will use the provided `Dockerfile`.

**Maintenance Action:**
- If you publish official images to Docker Hub or GHCR, set up a CI/CD pipeline to build and push the image automatically.
