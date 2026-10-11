"""MCP server exposing the FloodLens tools.

In-process (default): agents/agent.py connects over an in-memory MCP session.
Standalone over stdio (e.g. for an MCP-capable desktop agent):
    python -m agents.mcp_server
"""
import logging

from mcp.server.fastmcp import FastMCP

from agents.tools import flood_tools

logging.getLogger("mcp").setLevel(logging.WARNING)

mcp = FastMCP("floodlens-tools")
mcp.tool()(flood_tools.score_report)
mcp.tool()(flood_tools.lookup_guidance)
mcp.tool()(flood_tools.list_review_queue)

TOOL_NAMES = ["score_report", "lookup_guidance", "list_review_queue"]

if __name__ == "__main__":
    mcp.run()
