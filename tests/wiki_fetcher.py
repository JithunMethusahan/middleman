# wiki_fetcher.py
import os
import sys
# Tell Python to look in the parent directory for server.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import wikipedia
from mcp.server.fastmcp import FastMCP


# NOW you can import the server
from server import refine_output
# ... the rest of your code ...

mcp = FastMCP("Wiki-Raw")

@mcp.tool()
def get_raw_wiki(title: str) -> str:
    """
    Fetches the ENTIRE raw text of a Wikipedia page. 
    Warning: This returns a MASSIVE, unformatted block of text.
    """
    try:
        # We use a library that gets the raw content without cleaning
        page = wikipedia.page(title)
        return f"TITLE: {page.title}\n\nCONTENT:\n{page.content}"
    except Exception as e:
        return f"Error fetching Wikipedia: {str(e)}"

if __name__ == "__main__":
    mcp.run()