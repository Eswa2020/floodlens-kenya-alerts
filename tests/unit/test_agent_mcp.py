import anyio
from mcp.shared.memory import create_connected_server_and_client_session

from agents import agent
from agents.mcp_server import TOOL_NAMES, mcp


def test_mcp_server_exposes_tools():
    async def names():
        async with create_connected_server_and_client_session(mcp._mcp_server) as s:
            return sorted(t.name for t in (await s.list_tools()).tools)
    assert anyio.run(names) == sorted(TOOL_NAMES)


def test_agent_calls_tool_over_mcp():
    out = agent.handle({"text": "How do I know if we should evacuate?"})
    assert out["transport"] == "mcp" and out["tool"] == "lookup_guidance"


def test_review_queue_tool_returns_scores_not_text_or_photos():
    agent.handle({"text": "Call 0712 345 678, houses flooded at Kibera", "county": "Nairobi",
                  "image_tags": ["flooded_house"], "has_person": True, "photo_ref": "photos/x.jpg"})
    out = agent.handle({"text": "show queue"}, role="officer")
    item = out["result"]["items"][0]
    assert "text" not in item and "text_redacted" not in item and "photo_ref" not in item
    assert "evidence_score" in item
