# Copyright 2024 Jithun Methusahan - Apache License 2.0
import os, json, asyncio, sys
from openai import AsyncOpenAI
from mcp.server.fastmcp import FastMCP
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# 1. INITIALIZATION
mcp = FastMCP("Middleman-Pro-Gateway")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

# 2. HELPER: Load Config
def load_servers():
    config_path = os.path.join(os.getcwd(), "servers.json")
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return json.load(f)

# 3. CORE: Async Compressor
async def compress_text(text: str, focus_query: str) -> str:
    try:
        sys.stderr.write(f"[MIDDLEMAN] Compressing {len(text)} characters...\n")
        response = await client.chat.completions.create(
            model="google/gemini-1.5-flash",
            messages=[
                {"role": "system", "content": f"You are a Context Distiller. Extract only signal for: {focus_query}. Output XML <summary><core_facts>..."},
                {"role": "user", "content": text[:1000000]} # Limit to 1M chars
            ]
        )
        return response.choices[0].message.content or "<error>Empty AI response</error>"
    except Exception as e:
        return f"<error>Compression failed: {str(e)}</error>"

# 4. THE MASTER TOOL (With Metadata)
@mcp.tool()
async def delegate_and_refine(
    target_server: str, 
    target_tool: str, 
    tool_kwargs_json: str, 
    focus_query: str = "Summarize the key facts."
) -> str:
    """
    The Universal Proxy Gateway. Executes a tool on a downstream MCP server 
    and distills the results before returning them to the primary LLM.
    
    :param target_server: The key from servers.json (e.g., 'fetch', 'sqlite').
    :param target_tool: The specific tool name to call on the downstream server.
    :param tool_kwargs_json: A JSON string of arguments for the tool (e.g., '{"url": "https://..."}').
    :param focus_query: Specific information to extract from the raw data.
    """
    sys.stderr.write(f"\n[MIDDLEMAN] ROUTING: {target_server} -> {target_tool}\n")
    
    config = load_servers()
    if target_server not in config:
        return f"<error>Server '{target_server}' not configured in servers.json</error>"

    s = config[target_server]
    params = StdioServerParameters(command=s["command"], args=s["args"], env=os.environ.copy())
    
    try:
        kwargs = json.loads(tool_kwargs_json)
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(target_tool, arguments=kwargs)
                
                # Check for tool errors
                if getattr(result, 'is_error', False):
                    return f"<error>Downstream Error: {str(result.content)}</error>"

                # Extract and refine
                raw_text = "\n".join([c.text for c in result.content if hasattr(c, 'text')])
                return await compress_text(raw_text, focus_query)
    except Exception as e:
        return f"<error>Proxy Failed: {str(e)}</error>"

if __name__ == "__main__":
    mcp.run()