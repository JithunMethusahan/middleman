import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from mcp.server.fastmcp import FastMCP

# 1. Initialize the MCP Server
# FastMCP handles all the JSON-RPC / STDIO boilerplate for you.
mcp = FastMCP("ContextRefiner")

# 2. Configuration & Validation
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    # A real senior dev fails fast. Don't wait for a request to realize the key is missing.
    raise ValueError("FATAL: OPENROUTER_API_KEY environment variable is missing.")

# Initialize OpenRouter client using the standard OpenAI SDK structure
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# 3. Core Engine: The DOM Cleaner (No Regex Clowns Allowed)
def clean_html(html_content: str) -> str:
    """Strips garbage tags and extracts pure, structured text."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Kill Javascript, CSS, and structural garbage
    for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
        element.decompose()
        
    # Extract text, preserving some basic spacing
    text = soup.get_text(separator="\n", strip=True)
    return text

# 4. Core Engine: The OpenRouter Compressor
def compress_text(text: str, focus_query: str) -> str:
    """Sends the cleaned text to Gemini via OpenRouter to ruthlessly compress it."""
    
    # Truncate text to roughly ~800k characters (safety net for Gemini 1M token limit)
    # A robust app would use tiktoken here, but character slicing is a safe fallback for massive limits.
    max_chars = 3_000_000 
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[WARNING: TRUNCATED DUE TO EXTREME LENGTH]"

    system_prompt = f"""You are a ruthless Context Architect API. 
Your job is to read raw, messy scraped text and extract ONLY the high-value signal.

USER FOCUS QUERY: {focus_query}
Only extract information relevant to this query. Ignore EVERYTHING else.

RULES:
1. No fluff, no introductory text, no "Here is the summary".
2. Output STRICTLY in XML tags as defined below.
3. Preserve specific numbers, technical terms, and critical URLs.

OUTPUT SCHEMA:
<summary>
    <core_facts> (Bullet points of absolute truths found) </core_facts>
    <arguments> (Key arguments or consensus) </arguments>
    <urls> (List of important referenced links) </urls>
</summary>"""

    try:
        response = client.chat.completions.create(
            model="openrouter/free", # Fast, cheap, massive context window
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"RAW TEXT:\n{text}"}
            ],
            # Extra headers recommended by OpenRouter
            extra_headers={
                "HTTP-Referer": "https://github.com/mcp-context-refiner",
                "X-Title": "Universal Context Refiner MCP"
            }
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"<error>OpenRouter API Failure: {str(e)}</error>"


# 5. The MCP Tools (What the primary LLM actually sees and calls)

@mcp.tool()
def fetch_and_refine_url(url: str, focus_query: str = "Summarize the most important facts.") -> str:
    """
    ALWAYS use this tool when you have a URL instead of trying to read the page yourself.
    Fetches a web page, cleans the HTML, and aggressively compresses it based on your focus_query.
    Saves massive amounts of context window tokens.
    """
    try:
        # 10-second timeout. We don't hang forever.
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        raw_html = response.text
        cleaned_text = clean_html(raw_html)
        
        # If the page is completely empty after cleaning
        if len(cleaned_text.strip()) < 50:
            return "<error>Failed to extract meaningful text from URL.</error>"
            
        compressed_xml = compress_text(cleaned_text, focus_query)
        return compressed_xml
        
    except requests.exceptions.RequestException as e:
        return f"<error>Failed to fetch URL: {str(e)}</error>"

@mcp.tool()
def refine_raw_text(raw_text: str, focus_query: str) -> str:
    """
    Use this if you already have a massive block of raw text that needs compression.
    Warning: If the text is already in your context window, this wastes tokens. Prefer fetch_and_refine_url.
    """
    if not raw_text.strip():
        return "<error>Provided text was empty.</error>"
        
    return compress_text(raw_text, focus_query)

@mcp.tool()
def refine_local_file(file_path: str, focus_query: str) -> str:
    """
    Refines content from a local text or markdown file. 
    Use this for large documents or logs that the AI can't fit in its context.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content.strip()) < 10:
            return "<error>File is empty or too short.</error>"
            
        return compress_text(content, focus_query)
    except Exception as e:
        return f"<error>Failed to read file: {str(e)}</error>"
    
if __name__ == "__main__":
    # Runs the server over STDIO, which is required by Claude Desktop / Cursor
    mcp.run()