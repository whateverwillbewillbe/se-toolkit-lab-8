"""Stdio MCP server exposing LMS backend operations as typed tools."""

from __future__ import annotations

import asyncio
import json
import os
import urllib.request
from collections.abc import Awaitable, Callable, Sequence
from typing import Any
from urllib.parse import quote

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

from mcp_lms.client import LMSClient

_base_url: str = ""
_victorialogs_url: str = ""

server = Server("lms")

# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class _NoArgs(BaseModel):
    """Empty input model for tools that only need server-side configuration."""


class _LabQuery(BaseModel):
    lab: str = Field(description="Lab identifier, e.g. 'lab-04'.")


class _TopLearnersQuery(_LabQuery):
    limit: int = Field(
        default=5, ge=1, description="Max learners to return (default 5)."
    )


class _LogsSearchQuery(BaseModel):
    query: str = Field(
        default="*",
        description="LogsQL query string (e.g., 'level:error AND service:backend').",
    )
    limit: int = Field(default=10, ge=1, le=1000, description="Max logs to return.")


class _LogsErrorCountQuery(BaseModel):
    service: str = Field(default="", description="Service name to filter (optional).")
    hours: int = Field(
        default=1, ge=1, le=168, description="Time window in hours (max 7 days)."
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_api_key() -> str:
    for name in ("NANOBOT_LMS_API_KEY", "LMS_API_KEY"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    raise RuntimeError(
        "LMS API key not configured. Set NANOBOT_LMS_API_KEY or LMS_API_KEY."
    )


def _client() -> LMSClient:
    if not _base_url:
        raise RuntimeError(
            "LMS backend URL not configured. Pass it as: python -m mcp_lms <base_url>"
        )
    return LMSClient(_base_url, _resolve_api_key())


def _victorialogs_client() -> str:
    """Get VictoriaLogs base URL from environment."""
    url = _victorialogs_url or os.environ.get("VICTORIALOGS_URL", "")
    if not url:
        # Default to Docker internal network URL
        url = "http://victorialogs:9428"
    return url


def _query_victorialogs(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Query VictoriaLogs using LogsQL."""
    base_url = _victorialogs_client()
    encoded_query = quote(query, safe="")
    url = f"{base_url}/select/logsql/query?query={encoded_query}&limit={limit}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read().decode("utf-8")
            # VictoriaLogs returns newline-delimited JSON
            results = []
            for line in data.strip().split("\n"):
                if line:
                    results.append(json.loads(line))
            return results
    except Exception as e:
        return [{"error": f"VictoriaLogs query failed: {type(e).__name__}: {e}"}]


def _text(data: BaseModel | Sequence[BaseModel] | list[dict] | dict) -> list[TextContent]:
    """Serialize a pydantic model (or list of models/dicts) to a JSON text block."""
    if isinstance(data, dict):
        payload = data
    elif isinstance(data, list):
        payload = []
        for item in data:
            if isinstance(item, BaseModel):
                payload.append(item.model_dump())
            else:
                payload.append(item)
    elif isinstance(data, BaseModel):
        payload = data.model_dump()
    else:
        payload = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def _health(_args: _NoArgs) -> list[TextContent]:
    return _text(await _client().health_check())


async def _labs(_args: _NoArgs) -> list[TextContent]:
    items = await _client().get_items()
    return _text([i for i in items if i.type == "lab"])


async def _learners(_args: _NoArgs) -> list[TextContent]:
    return _text(await _client().get_learners())


async def _pass_rates(args: _LabQuery) -> list[TextContent]:
    return _text(await _client().get_pass_rates(args.lab))


async def _timeline(args: _LabQuery) -> list[TextContent]:
    return _text(await _client().get_timeline(args.lab))


async def _groups(args: _LabQuery) -> list[TextContent]:
    return _text(await _client().get_groups(args.lab))


async def _top_learners(args: _TopLearnersQuery) -> list[TextContent]:
    return _text(await _client().get_top_learners(args.lab, limit=args.limit))


async def _completion_rate(args: _LabQuery) -> list[TextContent]:
    return _text(await _client().get_completion_rate(args.lab))


async def _sync_pipeline(_args: _NoArgs) -> list[TextContent]:
    return _text(await _client().sync_pipeline())


# ---------------------------------------------------------------------------
# VictoriaLogs tool handlers
# ---------------------------------------------------------------------------


async def _logs_search(args: _LogsSearchQuery) -> list[TextContent]:
    """Search logs using LogsQL."""
    results = _query_victorialogs(args.query, args.limit)
    return _text(results)


async def _logs_error_count(args: _LogsErrorCountQuery) -> list[TextContent]:
    """Count errors per service over a time window."""
    # Build LogsQL query for errors (VictoriaLogs uses 'severity' field)
    if args.service:
        query = f'severity:ERROR AND service.name="{args.service}"'
    else:
        query = "severity:ERROR"
    # Query with a large limit to count all errors
    results = _query_victorialogs(query, limit=1000)
    # Count errors by service
    error_counts: dict[str, int] = {}
    for entry in results:
        service = entry.get("service.name", entry.get("service", "unknown"))
        error_counts[service] = error_counts.get(service, 0) + 1
    return _text([{"service": svc, "error_count": cnt} for svc, cnt in error_counts.items()])


# ---------------------------------------------------------------------------
# Registry: tool name -> (input model, handler, Tool definition)
# ---------------------------------------------------------------------------

_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]

_TOOLS: dict[str, _Registry] = {}


def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    # Pydantic puts definitions under $defs; flatten for MCP's JSON Schema expectation.
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (
        model,
        handler,
        Tool(name=name, description=description, inputSchema=schema),
    )


_register(
    "lms_health",
    "Check if the LMS backend is healthy and report the item count.",
    _NoArgs,
    _health,
)
_register("lms_labs", "List all labs available in the LMS.", _NoArgs, _labs)
_register(
    "lms_learners", "List all learners registered in the LMS.", _NoArgs, _learners
)
_register(
    "lms_pass_rates",
    "Get pass rates (avg score and attempt count per task) for a lab.",
    _LabQuery,
    _pass_rates,
)
_register(
    "lms_timeline",
    "Get submission timeline (date + submission count) for a lab.",
    _LabQuery,
    _timeline,
)
_register(
    "lms_groups",
    "Get group performance (avg score + student count per group) for a lab.",
    _LabQuery,
    _groups,
)
_register(
    "lms_top_learners",
    "Get top learners by average score for a lab.",
    _TopLearnersQuery,
    _top_learners,
)
_register(
    "lms_completion_rate",
    "Get completion rate (passed / total) for a lab.",
    _LabQuery,
    _completion_rate,
)
_register(
    "lms_sync_pipeline",
    "Trigger the LMS sync pipeline. May take a moment.",
    _NoArgs,
    _sync_pipeline,
)

# Register VictoriaLogs tools
_register(
    "logs_search",
    "Search logs using LogsQL. Use 'level:error' to find errors, 'service.name=\"backend\"' to filter by service.",
    _LogsSearchQuery,
    _logs_search,
)
_register(
    "logs_error_count",
    "Count errors per service over a time window. Returns error counts grouped by service name.",
    _LogsErrorCountQuery,
    _logs_error_count,
)


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main(base_url: str | None = None) -> None:
    global _base_url
    _base_url = base_url or os.environ.get("NANOBOT_LMS_BACKEND_URL", "")
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
