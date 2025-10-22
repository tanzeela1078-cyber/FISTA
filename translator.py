#!/usr/bin/env python3
"""
translator.py — Robust MCP client with dynamic initial input
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from agents.mcp.server import MCPServerStdio

# ---------- Configuration ----------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY not set — server may fail")

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT = os.path.join(HERE, "translator_server.py")
PYTHON_EXEC = sys.executable
CLIENT_SESSION_TIMEOUT_SECONDS = 30.0

# Model / RunConfig
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)
run_config = RunConfig(model=model, tracing_disabled=True)

async def run_agent_interaction(initial_input: str):
    """
    Launch MCP server, run Agent once for the given initial_input, cleanup.
    """
    params = {"command": PYTHON_EXEC, "args": [SERVER_SCRIPT]}
    async with MCPServerStdio(
        params=params,
        client_session_timeout_seconds=CLIENT_SESSION_TIMEOUT_SECONDS,
        name="local-translator",
    ) as mcp_server:
        print("✅ MCP server started and connected.")

        agent = Agent(
            name="GeminiVoiceAgent",
            instructions=(
                "You are a bilingual translator between English and Japanese. "
                "Translate or speak text using MCP tools."
            ),
            mcp_servers=[mcp_server],
        )

        runner = Runner()
        print("🚀 Running Agent with input:", initial_input)
        result = await runner.run(agent, initial_input, run_config)

        output_text = getattr(result, "final_output", result)
        print("💬 Agent Output:", output_text)
        return output_text
