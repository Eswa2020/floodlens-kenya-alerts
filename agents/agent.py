"""Agent: route the message, then call the matching tool through MCP.

The model part of the agent is a deterministic router in stub mode (no key,
no cost). Tool calls go over a real MCP client session (in-memory transport),
so the same tools can be served to any MCP-capable agent unchanged.
"""
import json
import logging

import anyio
from mcp.shared.memory import create_connected_server_and_client_session

from agents.mcp_server import mcp
from agents.router import route

ROUTE_TO_TOOL = {
    "flood_report": "score_report",
    "guidance_lookup": "lookup_guidance",
    "review_queue": "list_review_queue",
}
OFFICER_ONLY = {"review_queue"}

for noisy in ("mcp", "mcp.server", "mcp.server.lowlevel.server"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def build_args(route_name: str, message: dict) -> dict:
    if route_name == "flood_report":
        return {k: message[k] for k in ("text", "county", "language", "image_tags", "has_person", "photo_ref")
                if message.get(k) is not None}
    if route_name == "guidance_lookup":
        return {"question": message.get("text", "")}
    return {"limit": 20}


async def call_tool_mcp(tool: str, args: dict) -> dict:
    async with create_connected_server_and_client_session(mcp._mcp_server) as session:
        result = await session.call_tool(tool, args)
        if result.isError:
            raise RuntimeError(f"MCP tool {tool} failed: {result.content[0].text if result.content else ''}")
        return json.loads(result.content[0].text)


async def handle_async(message: dict, role: str = "reporter") -> dict:
    route_name = route(message.get("text", ""))
    if route_name in OFFICER_ONLY and role != "officer":
        return {"status": "forbidden", "route": route_name, "tool": None,
                "result": {"error": "the review queue is for duty officers only"}}
    tool = ROUTE_TO_TOOL[route_name]
    result = await call_tool_mcp(tool, build_args(route_name, message))
    return {"status": "ok", "route": route_name, "tool": tool, "transport": "mcp", "result": result}


def handle(message: dict, role: str = "reporter") -> dict:
    return anyio.run(handle_async, message, role)
