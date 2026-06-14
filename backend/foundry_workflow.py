"""Microsoft Foundry multi-agent workflow for LoopIn.

This module intentionally has no fallback model provider. Live mode uses
Microsoft Agent Framework with FoundryChatClient, Microsoft Learn MCP, and a
Foundry IQ knowledge-base MCP endpoint.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from contextlib import AsyncExitStack
from typing import Any

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential

LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"


def _text(result: Any) -> str:
    """Normalize Agent Framework results without depending on private fields."""
    value = getattr(result, "text", None)
    return value if isinstance(value, str) else str(result)


def _extract_json(text: str) -> dict[str, Any]:
    """Parse a JSON object even when the model wraps it in a markdown fence."""
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else text[text.find("{") : text.rfind("}") + 1]
    if not candidate:
        raise ValueError("Verifier Agent did not return a JSON object.")
    return json.loads(candidate)


async def run_foundry_workflow(profile: dict[str, Any]) -> dict[str, Any]:
    """Run the five-step opportunity-intelligence workflow and return JSON."""
    iq_mcp_url = os.environ.get("FOUNDRY_IQ_MCP_URL")
    if not iq_mcp_url:
        raise RuntimeError(
            "FOUNDRY_IQ_MCP_URL is required in live mode. Create a Foundry IQ "
            "knowledge base, expose its MCP endpoint, and set the URL securely."
        )

    credential = DefaultAzureCredential()
    client = FoundryChatClient(credential=credential)
    learn_tool = client.get_mcp_tool(
        name="Microsoft Learn MCP",
        url=LEARN_MCP_URL,
        approval_mode={
            "never_require_approval": [
                "microsoft_docs_search",
                "microsoft_docs_fetch",
            ]
        },
    )
    iq_tool = client.get_mcp_tool(
        name="LoopIn Foundry IQ",
        url=iq_mcp_url,
        approval_mode={"never_require_approval": ["knowledge_base_retrieve"]},
    )

    async with AsyncExitStack() as stack:
        profile_agent = await stack.enter_async_context(
            Agent(
                client=client,
                name="ProfileAnalyst",
                instructions=(
                    "You structure student opportunity profiles. Extract year, "
                    "location, current stack, goals, and interests. Never infer "
                    "sensitive personal information."
                ),
            )
        )
        curator_agent = await stack.enter_async_context(
            Agent(
                client=client,
                name="LearnCurator",
                instructions=(
                    "You search for current student-relevant signals: hackathons, "
                    "internships, developer tools, framework updates, learning paths, "
                    "and communities. Use Microsoft Learn MCP for Microsoft learning "
                    "and Foundry content. Use Foundry IQ to retrieve the LoopIn ranking "
                    "rubric. Return source URLs and never invent deadlines."
                ),
                tools=[learn_tool, iq_tool],
            )
        )
        planner_agent = await stack.enter_async_context(
            Agent(
                client=client,
                name="StudyPlanner",
                instructions=(
                    "You score and rank candidate signals by urgency, profile fit, "
                    "actionability, and source quality. Preserve every source URL."
                ),
            )
        )
        coach_agent = await stack.enter_async_context(
            Agent(
                client=client,
                name="ReadinessCoach",
                instructions=(
                    "You synthesize the strongest signals in a natural senior-friend "
                    "tone. Each card must explain what it is, why it matters to this "
                    "student, and exactly what to do next."
                ),
            )
        )
        verifier_agent = await stack.enter_async_context(
            Agent(
                client=client,
                name="SafetyVerifier",
                instructions=(
                    "You are the final critic. Reject unsupported claims, flag uncertain "
                    "deadlines for verification, ensure every card has a source URL, "
                    "and return only valid JSON."
                ),
            )
        )

        profile_result = await profile_agent.run(
            "Structure this student opportunity profile as concise JSON:\n"
            + json.dumps(profile, indent=2)
        )
        curated_result = await curator_agent.run(
            "Use your tools to retrieve current opportunities, tool updates, learning "
            "resources, and Microsoft-related signals for this structured profile:\n"
            + _text(profile_result)
        )
        plan_result = await planner_agent.run(
            "Rank the candidate signals from this grounded research.\nPROFILE:\n"
            + _text(profile_result)
            + "\nRESEARCH:\n"
            + _text(curated_result)
        )
        quiz_result = await coach_agent.run(
            "Synthesize the top 5-7 signals as senior-friend cards:\n"
            + _text(plan_result)
        )
        final_result = await verifier_agent.run(
            """
Audit the complete workflow below and return one JSON object with this schema:
{
  "mode": "Microsoft Foundry IQ + Web Search",
  "generatedAt": "ISO-8601 timestamp",
  "insights": [{
    "id": "string", "type": "Hackathon|Internship|Tool|Learning|Community|Open Source|Resource",
    "title": "string", "summary": "string", "source": "string",
    "sourceUrl": "https://...", "deadline": "string", "score": 0,
    "why": "string", "greeting": "string", "action": "string", "proof": "string"
  }],
  "trace": [{
    "key": "profile|search|rank|synthesis|verify",
    "agent": "string", "label": "string", "detail": "string",
    "tool": "string", "status": "completed", "decision": "string"
  }],
  "safety": ["string"]
}
Do not add markdown or commentary.

PROFILE OUTPUT:
"""
            + _text(profile_result)
            + "\nCURATOR OUTPUT:\n"
            + _text(curated_result)
            + "\nPLANNER OUTPUT:\n"
            + _text(plan_result)
            + "\nCOACH OUTPUT:\n"
            + _text(quiz_result)
        )

    await credential.close()
    return _extract_json(_text(final_result))


if __name__ == "__main__":
    sample = {
        "name": "Demo Student",
        "year": "Second year",
        "location": "India",
        "stacks": ["React", "Python"],
        "goals": ["Prepare for internships", "Win hackathons"],
        "interests": ["Hackathons", "AI agents", "Portfolio"],
    }
    print(json.dumps(asyncio.run(run_foundry_workflow(sample)), indent=2))
