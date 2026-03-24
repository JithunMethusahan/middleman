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
# limitations under the License
import asyncio
import os
import json
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# 1. CONFIGURATION
# Set your key here for the test
os.environ["OPENROUTER_API_KEY"] = "sk-or....."

async def run_proxy_test():
    print("🚀 STARTING UNIVERSAL PROXY TEST...")
    
    venv_python = "C:\\Users\\USER\\OneDrive\\Desktop\\programing\\context-refiner-mcp\\venv\\Scripts\\python.exe"
    server_script = "C:\\Users\\USER\\OneDrive\\Desktop\\programing\\context-refiner-mcp\\server.py"

    server_params = StdioServerParameters(
        command=venv_python,
        args=["-u", server_script],
        env=os.environ.copy()
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ CONNECTED TO MIDDLEMAN PROXY")

                target_args = json.dumps({"url": "https://en.wikipedia.org/wiki/Python_(programming_language)"})
                
                print("📡 DELEGATING FETCH TO DOWNSTREAM SERVER...")
                result = await session.call_tool(
                    "delegate_and_refine",
                    arguments={
                        "target_server": "fetch",
                        "target_tool": "fetch",
                        "tool_kwargs_json": target_args,
                        "focus_query": "Summary of the creation and early history of Python."
                    }
                )

                print("\nREFINED PROXY OUTPUT:")
                for content in result.content:
                    print(content.text)

    except ExceptionGroup as eg:
        # This is how we see what's INSIDE the TaskGroup error
        print("❌ DETAILED ERRORS:")
        for e in eg.exceptions:
            print(f"- {type(e).__name__}: {e}")
    except Exception as e:
        print(f"❌ GENERAL ERROR: {str(e)}")

if __name__ == "__main__":
    # Windows-specific fix for ProactorEventLoop if needed
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(run_proxy_test())