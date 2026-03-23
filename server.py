import os
from openai import OpenAI
from mcp.server.fastmcp import FastMCP

# Initialize
mcp = FastMCP("Middleman-Refiner")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("FATAL: OPENROUTER_API_KEY is missing.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def compress_text(text: str, focus_query: str) -> str:
    """The Core Distillation Engine."""
    # Safety: Limit to Gemini's massive but finite processing chunk
    max_chars = 1_500_000 
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[TRUNCATED]"

    system_prompt = f"""You are a 'Context Distiller'. You receive messy, high-volume output from other MCP tools.
Your goal: Transform raw data into a high-density XML summary.

USER FOCUS: {focus_query}

RULES:
1. Extract ONLY information relevant to the Focus Query.
2. Remove boilerplate, repetitive signatures, and 'noise'.
3. Maintain technical accuracy and preserve all unique URLs.
4. Output STRICTLY in <summary><core_facts>...</core_facts><urls>...</urls></summary> tags.
"""

    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"RAW MCP OUTPUT:\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"<error>Refinement Failed: {str(e)}</error>"

# server.py
@mcp.tool()
def refine_output(raw_text: str, source_tool: str, focus_query: str = "Summarize everything.") -> str:
    # This function now has THREE arguments. 
    # 1. raw_text
    # 2. source_tool
    # 3. focus_query
    if not raw_text.strip():
        return "<error>No content provided for refinement.</error>"
    
    return compress_text(f"SOURCE TOOL: {source_tool}\n\nCONTENT:\n{raw_text}", focus_query)

if __name__ == "__main__":
    mcp.run()