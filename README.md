# FX Rates MCP Server

A production-shaped [Model Context Protocol](https://modelcontextprotocol.io) server that gives
AI agents (Claude, ChatGPT, Cursor, and any MCP client) live and historical foreign-exchange rates.
Built by **[7Block Labs](https://7blocklabs.com)** as a public reference for how we ship MCP servers
for companies that sell data and APIs.

It runs on the free [Frankfurter](https://frankfurter.dev) API (European Central Bank reference rates,
no key required), so you can clone it and have a working MCP server in under a minute.

## Why this repo exists

Most "MCP servers" are an OpenAPI spec auto-converted into one tool per endpoint — which agents use
badly. This one is deliberately built the way a data/API company should ship theirs:

- **Task-shaped tools, not endpoint dumps.** Five tools that answer real questions
  (`convert_amount`, `latest_rates`, `historical_rate`, `timeseries`, `list_currencies`) instead of a
  raw mirror of the HTTP API.
- **Precise tool descriptions + read-only annotations** (`readOnlyHint`) so the model knows when and
  which tool to call — the difference between a demo and something agents use reliably.
- **Streamable HTTP transport** (MCP spec 2025-06-18 and later), ready to deploy as a remote server.
- **A clean seam for auth + plan entitlements.** For a paid data API this is where per-user OAuth 2.1,
  plan → scope mapping, rate limits, and usage metering attach. See [`docs/PRODUCTION.md`](docs/PRODUCTION.md).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Local (stdio) — for Claude Desktop / Cursor:
python -m fx_mcp.server

# Remote (Streamable HTTP) — for hosting:
TRANSPORT=http PORT=8000 python -m fx_mcp.server
```

### Use it in Claude Code

```bash
claude mcp add --transport http fx-rates http://localhost:8000/mcp
```

### Use it in Claude Desktop / Cursor (stdio)

```json
{
  "mcpServers": {
    "fx-rates": { "command": "python", "args": ["-m", "fx_mcp.server"] }
  }
}
```

## Tools

| Tool | What it answers |
|------|-----------------|
| `convert_amount` | "How much is 100 USD in EUR?" (latest or on a date) |
| `latest_rates` | Today's ECB rates for a base against some/all currencies |
| `historical_rate` | Rates on a specific past date |
| `timeseries` | A daily series over a range (for trends / charts) |
| `list_currencies` | All supported currency codes + names |

## From reference to your production server

This is the free-data version. For a company selling a paid data API, the same architecture extends to:
account linking (OAuth 2.1 into your existing logins), plan-aware entitlements and rate limits, usage
metering into your billing, an in-chat UI, and listing in the Claude and ChatGPT directories.

That's what we do. **[7Block Labs](https://7blocklabs.com)** builds and launches MCP servers for
data and API companies — [get in touch](https://7blocklabs.com).

## License

MIT — see [LICENSE](LICENSE).
