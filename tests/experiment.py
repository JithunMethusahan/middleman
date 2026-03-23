import sys
import os
# Tell Python to look in the parent directory for server.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tiktoken # To count real tokens
from server import refine_output
from wiki_fetcher import get_raw_wiki


# NOW you can import the server
from server import refine_output
# ... the rest of your code ...

# 1. SETUP
os.environ["OPENROUTER_API_KEY"] = "sk-or......"
encoding = tiktoken.get_encoding("cl100k_base") # The GPT-4/Gemini tokenizer

def run_benchmark(wiki_topic: str, focus: str):
    print(f"\n🚀 STARTING BENCHMARK: {wiki_topic}")
    print("-" * 50)

    # 2. THE FETCH (The "Messy" Stage)
    raw_data = get_raw_wiki(wiki_topic)
    raw_tokens = len(encoding.encode(raw_data))
    
    print(f"RAW DATA FETCHED: {raw_tokens} tokens.")

    # 3. THE REFINEMENT (The "Middleman" Stage)
    print(f"REFINING FOR: '{focus}'...")
    
    # We simulate the AI passing the raw data to Middleman
    refined_xml = refine_output(raw_data, "Wiki-Raw-Tool", focus)
    refined_tokens = len(encoding.encode(refined_xml))

    # 4. THE RESULTS
    reduction = ((raw_tokens - refined_tokens) / raw_tokens) * 100
    
    print("-" * 50)
    print(f"REFINED DATA:\n{refined_xml}")
    print("-" * 50)
    print(f"✅ RAW TOKENS: {raw_tokens}")
    print(f"✅ REFINED TOKENS: {refined_tokens}")
    print(f"📉 REDUCTION: {reduction:.2f}%")
    print(f"💰 ESTIMATED SAVINGS: You just saved the primary LLM {raw_tokens - refined_tokens} tokens of context.")

if __name__ == "__main__":
    # Test on a heavy topic: "Artificial Intelligence"
    run_benchmark("Artificial intelligence", "What are the specific risks mentioned regarding AGI?")