# Taking this to production for a paid data API

This reference server runs on a free, keyless API. When we build the same for a company that **sells**
data or API access, the tool layer stays; these layers get added. They are also the layers that
generators and API-gateway "REST→MCP" features do **not** handle — the reason a data company hires us.

## 1. Account linking (OAuth 2.1)
- The user clicks *Connect* in Claude/ChatGPT and logs into **your** existing account system.
- MCP authorization spec: OAuth 2.1, Protected Resource Metadata (RFC 9728), Client ID Metadata
  Documents (preferred; dynamic client registration is deprecated), resource indicators (RFC 8707),
  `iss` validation (RFC 9207), PKCE.
- API-key fallback for power users in Claude Code / Cursor.

## 2. Plan entitlements + rate limits
- Map the caller's plan → which tools/scopes they can use; **step-up** when a tool needs a higher tier.
- Per-tenant rate limits (never one global bucket).
- Return partial results + a clear "upgrade for full history" signal instead of a hard 403.

## 3. Usage metering + billing
- Meter each call back into your existing billing (per-call, credits, or plan-included).
- Optional agent-native payments (Stripe, x402) for callers with no account.

## 4. Transport + scale
- Streamable HTTP, stateless per the 2026-07-28 spec (no protocol-level session to lose).
- Deploy on your cloud or serverless (Cloudflare Workers, AWS, Vercel, Azure).

## 5. Distribution
- Submit to the **Claude** connectors directory (OAuth, tool annotations, test account, example prompts).
- Submit to the **ChatGPT** apps directory (domain verification, test cases per tool).
- Publish `server.json` to the official **MCP Registry**; list on Smithery / PulseMCP / Glama; add
  one-click install to your docs.

## 6. Security review
- No token passthrough, prompt-injection / tool-poisoning tests, audit logging, least-privilege scopes.

---
Built by [7Block Labs](https://7blocklabs.com) — MCP servers for data & API companies.
