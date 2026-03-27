# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**Q: "What is the agentic loop?"**

The agentic loop is the core iterative cycle that an autonomous AI agent follows to accomplish tasks. It typically consists of these key stages:

**The Loop**

1. **Perceive** — Gather information from the environment (user input, tool outputs, observations)
2. **Think/Reason** — Process the information, plan next steps, make decisions
3. **Act** — Execute actions (call tools, modify files, send messages, run commands)
4. **Observe** — Receive feedback from the actions taken
5. **Repeat** — Continue the cycle until the goal is achieved or a stopping condition is met

**Why It Matters**

This loop enables agents to:

- Handle multi-step tasks autonomously
- Adapt based on feedback and changing conditions
- Recover from errors by trying alternative approaches
- Break complex problems into manageable steps

**Q: "What labs are available in our LMS?"**

The agent responded that it doesn't have access to the LMS:

> "I don't see any specific information about your LMS (Learning Management System) in the workspace memory. To help you find available labs, I would need to know:
>
> 1. Which LMS are you using? (e.g., Canvas, Moodle, Blackboard, Coursera, edX, a custom university portal, etc.)
> 2. Do you have API access or a way to query your LMS? Some LMS platforms have APIs that can be accessed with proper authentication.
> 3. Is there a specific course or context you're looking for labs in?"

This is expected — the bare agent has no tools connected to the LMS backend.

## Task 1B — Agent with LMS tools

**Q: "What labs are available?"**

The agent successfully queried the LMS using MCP tools and returned:

> "Great! The sync completed and now there are 7 labs available in your LMS:
>
> | ID | Title |
> |---|---|
> | 1 | Lab 01 – Products, Architecture & Roles |
> | 2 | Lab 02 — Run, Fix, and Deploy a Backend Service |
> | 3 | Lab 03 — Backend API: Explore, Debug, Implement, Deploy |
> | 4 | Lab 04 — Testing, Front-end, and AI Agents |
> | 5 | Lab 05 — Data Pipeline and Analytics Dashboard |
> | 6 | Lab 06 — Build Your Own Agent |
> | 7 | Lab 07 — Build a Client with an AI Coding Agent |"

**Q: "Describe the architecture of the LMS system"**

The agent provided a detailed architecture description including:

- **High-Level Components**: Caddy (reverse proxy), FastAPI Backend, PostgreSQL Database, Nanobot AI Agent, pgAdmin
- **Core Components**:
  - Caddy serves React frontend and proxies API requests
  - FastAPI Backend with layered architecture (Routers → Auth Middleware → Database → Models)
  - PostgreSQL with OBER-compatible schema (item, learner, interacts tables)
  - Nanobot with WebSocket gateway, MCP tools, skills system, memory, and cron jobs
- **Design Decisions**: Monolith for simplicity, Caddy for single-origin, SQLModel for ORM+validation, async DB, feature flags
- **Key Interaction Flows**: Student browsing, AI agent queries, Telegram messaging

## Task 1C — Skill prompt

**Q: "Show me the scores" (without specifying a lab)**

The agent responded with a comprehensive overview of all lab scores:

> "Here are the scores and pass rates for all 7 labs:
>
> [Detailed table showing all labs with Task, Avg Score, and Attempts columns]
>
> **Key Insights:**
>
> - Highest performing tasks: Lab 01 - Lab setup (84.3%), Lab 07 - Plan and Scaffold (76.9%)
> - Most attempted tasks: Lab 01 - Lab setup (2,931 attempts), Lab 06 - The System Agent (2,051 attempts)
> - Lowest performing tasks: Lab 02 - Make your VM a proxy (0.0%), Lab 01 - Plan skill development (20.0%)
>
> Would you like me to show completion rates, top learners, or submission timelines for any specific lab?"

The skill prompt teaches the agent to:

- Format numeric results nicely (percentages with one decimal, counts with commas)
- Keep responses structured with tables and bullet points
- Offer relevant follow-up questions after providing data
- Explain available tools when asked "what can you do?"

## Task 2A — Deployed agent

Nanobot gateway startup log excerpt:

```
nanobot-1  | Using config: /app/nanobot/config.resolved.json
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | 2026-03-27 02:06:46.535 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms': connected, 9 tools registered
nanobot-1  | 2026-03-27 02:06:46.535 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

The gateway started successfully with 9 LMS MCP tools registered.

## Task 2B — Web client

**WebSocket endpoint test:**

The WebSocket endpoint at `ws://localhost:42002/ws/chat?access_key=quaaow` is working. Test query "What labs are available?" returned:

> "Here are the available labs:
>
> 1. **Lab 01** – Products, Architecture & Roles
> 2. **Lab 02** — Run, Fix, and Deploy a Backend Service
> 3. **Lab 03** — Backend API: Explore, Debug, Implement, Deploy
> 4. **Lab 04** — Testing, Front-end, and AI Agents
> 5. **Lab 05** — Data Pipeline and Analytics Dashboard
> 6. **Lab 06** — Build Your Own Agent
> 7. **Lab 07** — Build a Client with an AI Coding Agent
>
> Would you like more details about any specific lab, such as pass rates, completion stats, or top learners?"

**Flutter web client:**

The Flutter web client is accessible at <http://localhost:42002/flutter/>. It shows a login screen that requires the `NANOBOT_ACCESS_KEY` (quaaow) to authenticate.

To test:

1. Open <http://localhost:42002/flutter/> in a browser
2. Enter the access key: `quaaow`
3. Ask questions like "What can you do in this system?" or "Which lab has the lowest pass rate?"

## Task 3A — Structured logging

**Happy-path log excerpt** (request_started → request_completed with status 200):

```
backend-1  | 2026-03-27 02:29:22,199 INFO [app.main] - request_started
backend-1  | 2026-03-27 02:29:22,200 INFO [app.auth] - auth_success
backend-1  | 2026-03-27 02:29:22,200 INFO [app.db.items] - db_query
backend-1  | 2026-03-27 02:29:22,205 INFO [app.main] - request_completed
```

**Error-path log excerpt** (db_query with error when PostgreSQL is stopped):

```
backend-1  | socket.gaierror: [Errno -2] Name or service not known
backend-1  | During handling of the above exception, another exception occurred:
backend-1  | TypeError: unhandled_exception_handler() takes 1 positional argument but 2 were given
```

**VictoriaLogs query result:**

Querying `http://localhost:42010/select/logsql/query?query=*&limit=5` returns structured JSON logs with fields:

- `_msg`: Log message
- `severity`: INFO/ERROR
- `service.name`: Service identifier
- `event`: Event name (request_started, auth_success, db_query)
- `trace_id`: Distributed trace ID
- `span_id`: Span identifier
- `error`: Error message (for ERROR severity)

## Task 3B — Traces

**VictoriaTraces status:**

Traces are being stored (55,806+ rows in storage) but the Jaeger API endpoints aren't enabled in this VictoriaTraces version. The traces can be viewed through the web UI at `http://localhost:42011/select/vmui/`.

**Trace data available:**

- `trace_id`: Links related spans across services
- `span_id`: Individual operation identifier
- `otelServiceName`: Service name (Learning Management Service)
- `otelTraceSampled`: Sampling flag

## Task 3C — Observability MCP tools

**MCP tools implemented:**

| Tool | Description |
|------|-------------|
| `logs_search` | Search logs using LogsQL (query, limit) |
| `logs_error_count` | Count errors per service (service, hours) |

**Agent response under normal conditions:**

> "Good news! **No errors** in the last hour. Both the error count check and log search returned empty results, so the system has been running cleanly."

**Agent response under failure conditions (PostgreSQL stopped):**

The agent uses `logs_error_count` and `logs_search` tools to check for errors. Note: The agent initially used `level:error` instead of `severity:ERROR` (VictoriaLogs field name). After updating the skill prompt, the agent correctly queries for errors.

**Files created:**

- `mcp/mcp_lms/server.py` - Added `logs_search` and `logs_error_count` tools
- `nanobot/workspace/skills/observability/SKILL.md` - Observability skill prompt

## Task 4 — Bug investigation

### Investigation Transcript

**Q1: "Show me recent errors"**

Agent response:
> "Good news! The initial error search returned **no recent errors** in the system logs.
>
> However, I encountered a technical issue when trying to do broader log searches - there appears to be a backend bug with the logs search tool (`AttributeError: 'dict' object has no attribute 'model_dump'`).
>
> The LMS system itself is **healthy** with 50 items in the database."

**Q2: "Any errors now?"** (after initial fix attempt)

Agent response:
> "Yes, there are some errors:
>
> 1. **Learning Management Service**: 8 errors in the past hour
> 2. **Backend Service**: VictoriaLogs query failure - `HTTP Error 400: Bad Request`"

### Root Cause

The bug was in the `_text()` helper function in `mcp/mcp_lms/server.py`. This function was designed to serialize Pydantic `BaseModel` objects, but my new VictoriaLogs MCP tools (`logs_search` and `logs_error_count`) return plain Python `dict` objects from JSON parsing.

When `_text()` tried to call `item.model_dump()` on a dict, it raised:

```
AttributeError: 'dict' object has no attribute 'model_dump'
```

**Original code:**

```python
def _text(data: BaseModel | Sequence[BaseModel]) -> list[TextContent]:
    """Serialize a pydantic model (or list of models) to a JSON text block."""
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    else:
        payload = [item.model_dump() for item in data]
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
```

### Fix

Updated `_text()` to handle both Pydantic models and plain dicts:

```python
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
```

**File changed:** `mcp/mcp_lms/server.py` (lines 108-123)

### Verification

**Q: "Any errors in the last 5 minutes?"**

Agent response:
> "**No errors in the last 5 minutes.** ✅
>
> However, there were **8 errors in the last hour** from the Learning Management Service.
>
> The logs search tool is now working correctly."

The 8 errors from the last hour were from earlier testing when PostgreSQL was stopped intentionally - not from the bug.

## Task 5A — Multi-step investigation

<!-- Paste the agent's response to "what went wrong?" showing chained log+trace queries -->

## Task 5B — Cron health check

<!-- Screenshot of the health report in the Flutter app -->
