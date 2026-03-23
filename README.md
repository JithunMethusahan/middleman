<div align="center">

  <img src="assets/icon (1).png" alt="icon (1).png" width="150" height="150" />

  <h1>Middleman: The Context Refiner MCP 🚀</h1>
  <p><em>Enterprise-grade context distillation for LLMs. Cut API costs by 95%.</em></p>
</div>


Middleman is an enterprise-grade Model Context Protocol (MCP) server designed to act as a "Signal Filter" between messy raw data and expensive LLMs.
It gets another MCP output (e.g., Wikipedia) before going to the AI, summarizes it, and sends it to the AI to save tokens.


![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![MCP Supported](https://img.shields.io/badge/MCP-Supported-blue)


### Real-World Impact

| Source Data              | Raw Tokens | Middleman Signal | Token Reduction | Cost Savings |
|--------------------------|------------|------------------|-----------------|--------------|
| Wikipedia (Full Article) | ~25,000    | ~800             | 96.8%           | 💰💰💰      |
| Reddit Discussion        | ~15,000    | ~600             | 96%             | 💰💰💰      |
| System Logs (5MB)        | ~500,000   | ~1,200           | 99.7%           | 💰💰💰      |

---

## ✨ Key Features

- **URL Fetch & Refine:** Scrapes web pages, strips the DOM of garbage, and extracts the core facts.
- **Local File Processing:** High-density distillation of local `.txt`, `.log`, and `.md` files.
- **Surgical Focus Query:** Tell Middleman exactly what you are looking for (e.g., *"Focus only on the technical specs of the Starship engine"*) to ensure the summary is relevant.
- **XML-Structured Output:** Returns data in a strict `<summary><core_facts>...</core_facts></summary>` schema, optimized for machine-to-machine communication.
- **Built on FastMCP:** Robust, Pythonic implementation of the Model Context Protocol.

---

## 🛠️ Technical Stack

| Component      | Technology                              |
|----------------|-----------------------------------------|
| Runtime        | Python 3.10+                            |
| Protocol       | MCP (Model Context Protocol)            |
| Primary Engine | Google Gemini-1.5-Flash (via OpenRouter)|
| Scraper        | BeautifulSoup4 (LXML)                   |
| Orchestration  | FastMCP                                 |

---

## 🚀 Installation & Setup

### 1. Prerequisites

- Python 3.10 or higher
- An [OpenRouter API Key](https://openrouter.ai/)

### 2. Clone and Install

```bash
git clone https://github.com/JithunMethusahan/middleman.git
cd middleman
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Set your API key in your environment:

```bash
export OPENROUTER_API_KEY="your_key_here"
# Windows: $env:OPENROUTER_API_KEY="your_key_here"
```

### 4. Integration with Claude Desktop / Cursor

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "middleman": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["/path/to/middleman/server.py"],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-..."
      }
    }
  }
}
```

---

## 📖 Usage Examples

### Tool: `fetch_and_refine_url`

**Input:**
- `url`: `"https://en.wikipedia.org/wiki/Quantum_computing"`
- `focus_query`: `"What is Shor's algorithm?"`

**Output:**

```xml
<summary>
    <core_facts>
        - Shor's algorithm is a quantum algorithm for integer factorization.
        - It runs exponentially faster than the best known classical algorithm.
    </core_facts>
    <urls>
        - https://en.wikipedia.org/wiki/Shor%27s_algorithm
    </urls>
</summary>
```

---

## 🤝 Contributing & Customization

Middleman is designed to be extensible. Want to add support for PDFs, YouTube transcripts, or SQL databases?

1. Fork the repo.
2. Add your tool to `server.py`.
3. Submit a Pull Request.

For custom enterprise integrations or consulting, contact the author via [GitHub Issues](https://github.com/JithunMethusahan/middleman/issues).

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
