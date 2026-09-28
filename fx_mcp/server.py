"""
FX Rates MCP Server — a 7Block Labs reference build.

A production-shaped Model Context Protocol server over the free Frankfurter FX API
(https://frankfurter.dev, ECB reference rates, no API key). It exists to demonstrate how we
build MCP servers for data/API companies:

  * task-shaped tools (a few tools that answer real questions), not one tool per endpoint
  * read-only tool annotations + precise descriptions so agents call the right tool
  * Streamable HTTP transport (MCP spec 2025-06-18+), ready to host remotely
  * a clean seam where per-user OAuth + plan entitlements would attach for a paid data API

Run locally (stdio):      python -m fx_mcp.server
Run remote (HTTP):        TRANSPORT=http PORT=8000 python -m fx_mcp.server
"""
from __future__ import annotations

import os
from datetime import date

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

API = "https://api.frankfurter.dev/v1"
USER_AGENT = "fx-mcp/1.0 (+https://github.com/7BlockLabs/mcp-fx-reference)"

mcp = MCPServer(
    "FX Rates",
    instructions=(
        "Foreign-exchange reference rates from the European Central Bank via Frankfurter. "
        "Use convert_amount for 'how much is X in Y', latest_rates for today's rates, "
        "historical_rate for a past date, and timeseries for a range. Rates are ECB reference "
        "rates published on business days; weekends/holidays resolve to the last business day."
    ),
)

READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=True)


async def _get(path: str, params: dict) -> dict:
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": USER_AGENT}) as c:
        r = await c.get(f"{API}{path}", params=params)
        r.raise_for_status()
        return r.json()


@mcp.tool(
    title="Convert an amount between currencies",
    description="Convert a money amount from one currency to another using the latest ECB rate "
    "(or a specific date). Returns the converted amount and the rate used. Example: "
    "convert_amount(amount=100, base='USD', quote='EUR').",
    annotations=READ_ONLY,
)
async def convert_amount(amount: float, base: str, quote: str, on: str | None = None) -> dict:
    """amount: money to convert. base/quote: 3-letter ISO codes. on: optional YYYY-MM-DD."""
    base, quote = base.upper(), quote.upper()
    path = f"/{on}" if on else "/latest"
    data = await _get(path, {"base": base, "symbols": quote, "amount": amount})
    rate = data["rates"].get(quote)
    if rate is None:
        return {"error": f"no rate for {base}->{quote}", "available": list(data["rates"])}
    return {"amount": amount, "base": base, "quote": quote, "converted": rate,
            "rate": round(rate / amount, 6) if amount else None, "date": data["date"]}


@mcp.tool(
    title="Latest exchange rates",
    description="Get today's ECB reference rates for one base currency against some or all "
    "currencies. Example: latest_rates(base='EUR', symbols=['USD','GBP']).",
    annotations=READ_ONLY,
)
async def latest_rates(base: str = "EUR", symbols: list[str] | None = None) -> dict:
    params = {"base": base.upper()}
    if symbols:
        params["symbols"] = ",".join(s.upper() for s in symbols)
    return await _get("/latest", params)


@mcp.tool(
    title="Historical rate on a date",
    description="Get ECB reference rates for a specific past date (YYYY-MM-DD). Weekends/holidays "
    "return the most recent prior business day. Example: historical_rate('2020-01-02', base='USD').",
    annotations=READ_ONLY,
)
async def historical_rate(on: str, base: str = "EUR", symbols: list[str] | None = None) -> dict:
    params = {"base": base.upper()}
    if symbols:
        params["symbols"] = ",".join(s.upper() for s in symbols)
    return await _get(f"/{on}", params)


@mcp.tool(
    title="Rate time series over a range",
    description="Get a daily time series of rates between two dates for a base/quote pair. Useful "
    "for trends or charts. Example: timeseries('2024-01-01','2024-01-31', base='USD', quote='INR').",
    annotations=READ_ONLY,
)
async def timeseries(start: str, end: str | None, base: str, quote: str) -> dict:
    end = end or date.today().isoformat()
    data = await _get(f"/{start}..{end}", {"base": base.upper(), "symbols": quote.upper()})
    series = {d: r.get(quote.upper()) for d, r in sorted(data.get("rates", {}).items())}
    return {"base": base.upper(), "quote": quote.upper(), "start": start, "end": end,
            "points": len(series), "series": series}


@mcp.tool(
    title="List supported currencies",
    description="List all currency codes the service supports, with their full names.",
    annotations=READ_ONLY,
)
async def list_currencies() -> dict:
    return await _get("/currencies", {})


def main() -> None:
    transport = os.environ.get("TRANSPORT", "stdio")
    if transport == "http":
        import uvicorn
        uvicorn.run(mcp.streamable_http_app(), host="0.0.0.0",
                    port=int(os.environ.get("PORT", "8000")))
    else:
        mcp.run()


if __name__ == "__main__":
    main()
