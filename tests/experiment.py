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