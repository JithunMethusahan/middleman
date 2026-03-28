# Copyright 2024 Jithun Methusahan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import asyncio
from openai import AsyncOpenAI
from mcp.server.fastmcp import FastMCP
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# 1. INITIALIZATION
mcp = FastMCP("Middleman")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("FATAL: OPENROUTER_API_KEY is missing.")

# Notice we use AsyncOpenAI now because this is an async proxy
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# 2. LOAD PLUGINS (The Gateway Config)
def load_servers():
    config_path = os.path.join(os.path.dirname(__file__), "servers.json")
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return json.load(f)

# 3. THE COMPRESSOR ENGINE (Async)
async def compress_text(text: str, focus_query: str) -> str:
    max_chars = 1_500_000 
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[TRUNCATED]"

    system_prompt = f"""You are the Middleman Context Distiller.
You receive massive, raw data dumps from downstream MCP servers (Databases, APIs, Scrapers).
Extract ONLY the signal requested in the USER FOCUS.
USER FOCUS: {focus_query}
Output STRICTLY in <summary><core_facts>...</core_facts></summary> tags."""

    try:
        response = await client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"RAW MCP OUTPUT:\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"<error>Compression Failure: {str(e)}</error>"

# 4. THE UNIVERSAL PROXY TOOL
import sys # Add this to your imports at the top

@mcp.tool()
async def delegate_and_refine(target_server: str, target_tool: str, tool_kwargs_json: str, focus_query: str) -> str:
    """
    UNIVERSAL PROXY GATEWAY: Executes downstream tools and refines output.
    """
    servers_config = load_servers()
    
    if target_server not in servers_config:
        return f"<error>Server '{target_server}' not found.</error>"

    server_info = servers_config[target_server]
    command = server_info.get("command")
    args = server_info.get("args", [])

    try:
        kwargs = json.loads(tool_kwargs_json)
    except json.JSONDecodeError:
        return "<error>Invalid JSON in tool_kwargs_json.</error>"

    try:
        # Use stderr for logging - it's invisible to the MCP protocol
        sys.stderr.write(f"DEBUG: Launching {target_server}...\n")
        
        server_params = StdioServerParameters(
            command=command, 
            args=args,
            env=os.environ.copy()
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # 1. CALL THE TOOL
                result = await session.call_tool(target_tool, arguments=kwargs)
                
                # 2. CHECK FOR DOWNSTREAM ERRORS
                if getattr(result, "is_error", False):
                    # Downstream tool failed, return its error message
                    err_msg = "\n".join([c.text for c in result.content if hasattr(c, 'text')])
                    return f"<error>Downstream Tool Error: {err_msg}</error>"

                # 3. EXTRACT TEXT CONTENT (Harden the extraction)
                raw_chunks = []
                for content in result.content:
                    if hasattr(content, 'text') and content.text:
                        raw_chunks.append(content.text)
                
                raw_output = "\n".join(raw_chunks)
                
                if not raw_output.strip():
                    return f"<error>Target tool {target_tool} returned no text content.</error>"

                # 4. COMPRESS
                sys.stderr.write(f"DEBUG: Compressing {len(raw_output)} chars...\n")
                refined_xml = await compress_text(raw_output, focus_query)
                
                # FINAL SAFETY: Ensure we never return None
                return str(refined_xml) if refined_xml is not None else "<error>Compression returned None</error>"

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        return f"<error>Proxy Execution Failed: {str(e)}</error>"

# ... (keep all your existing imports and tools) ...

if __name__ == "__main__":
    import sys
    # If you run: python server.py
    # It runs locally for Claude/Cursor
    if len(sys.argv) == 1:
        mcp.run(transport="stdio")
    
    # If you run: python server.py sse
    # It starts a Web Server for Smithery/Render
    elif sys.argv[1] == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Route
        import uvicorn

        sse = SseServerTransport("/messages")
        app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=sse.handle_sse),
                Route("/messages", endpoint=sse.handle_post_message, methods=["POST"]),
            ],
        )

        async def handle_mcp():
            async with mcp._mcp_server as server:
                await server.connect(sse)

        @app.on_event("startup")
        async def startup():
            asyncio.create_task(handle_mcp())

        # Render provides the PORT environment variable
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)