#!/usr/bin/env python3
"""
translator_server.py — Local MCP server that performs text translation using Gemini via REST API
Uses FastMCP with correct run() call.
"""

import os
import asyncio
import logging
import aiohttp
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from langdetect import detect


# Setup
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY must be set")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

mcp = FastMCP("live-translator-server")
@mcp.tool()
async def detect_language(text: str) -> str:
    """Detect language code (en, ja, etc.)"""
    try:
        lang = detect(text)
        return lang
    except Exception as e:
        return f"Error detecting language: {e}"

@mcp.tool()
async def translate_text(text: str, source_lang: str = "English", target_lang: str = "Japanese") -> str:
    try:
        logging.info(f"Translating {source_lang}→{target_lang}: {text}")
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "gemini-2.0-flash",
                "messages": [
                    {"role": "system", "content": f"You are a translator from {source_lang} to {target_lang}."},
                    {"role": "user", "content": text}
                ],
            }
            params = {"key": GEMINI_API_KEY}
            async with session.post(GEMINI_URL, json=payload, params=params) as resp:
                if resp.status != 200:
                    err = await resp.text()
                    logging.error(f"API error: {err}")
                    return f"Translation failed: {resp.status}"
                data = await resp.json()
                translation = data["choices"][0]["message"]["content"]
                logging.info(f"Translation result: {translation}")
                return translation
    except Exception as e:
        logging.exception("Exception during translation")
        return f"Error: {str(e)}"

@mcp.tool()
async def ping() -> str:
    return "✅ Translator MCP server is alive"

if __name__ == "__main__":
    print("🚀 Starting Translator MCP Server …")
    mcp.run()
