# debug_test.py
import os
from server import clean_html, compress_text, fetch_and_refine_url

# MANUALLY SET YOUR KEY HERE FOR THE TEST IF ENV VAR IS FAILING
# os.environ["OPENROUTER_API_KEY"] = "your-key-here"

print("--- TESTING SCRAPER AND CLEANER ---")
test_url = "https://en.wikipedia.org/wiki/SpaceX"
result = fetch_and_refine_url(test_url, "What is the mission of SpaceX?")

print("\nRESULT FROM GEMINI:")
print(result)