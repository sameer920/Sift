# 🚀 Google SERP Scraper

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/powered%20by-Playwright-green.svg)](https://playwright.dev/)




A powerful, stealthy, and localized Google Search Result Page (SERP) scraper. Designed as a **free, self-hosted alternative to Serper.dev**, this tool is built specifically for AI agents and developers who need high-quality search data without the API costs.

---

## ✨ Features

- **Full SERP Coverage**: Extracts Organic Results, People Also Ask (PAA), and Related Searches.
- **AI Overview Support**: Deep extraction of Google's AI Overviews, including full text and source links.
- **Stealth by Default**: Powered by `Camoufox`, a specialized Playwright-based browser that bypasses most bot detection.
- **Persistent Sessions**: Uses a local `.browser_profile` to store cookies and session data, enabling you to bypass CAPTCHAs.
- **Human-like interactions**: Random delays and timeouts between actions as well as human-like mouse movements and scrolling.

---

## 🏗 Project Structure

```text
googleSerpScraper/
├── scraper.py           # Main CLI entry point and orchestration logic
├── browser/
│   └── manager.py       # Camoufox/Playwright context management
├── extraction/
│   ├── parsers.py       # Core logic for parsing SERP HTML elements
│   └── utils.py         # Helper functions (delays, URL cleaning, date parsing)
├── config/
│   └── settings.py      # Scraper configuration (timeouts, retry limits)
└── .browser_profile/    # Local browser session data (Git ignored)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Playwright browsers installed

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/googleSerpScraper.git
   cd googleSerpScraper
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the browser engine:
   ```bash
   playwright install firefox
   ```

### Basic Usage
Run the scraper directly from the command line:
```bash
python scraper.py "how to build an ai agent" --num 10
```

---

## 🛠 Upcoming Features (Roadmap)

We are actively building this to be the backbone of local agentic workflows:
- [ ] **Local API Server**: A FastAPI-based wrapper to provide a Serper-compatible JSON endpoint locally.
- [ ] **AI Overview Interface**: A dedicated UI for exploring extracted AI Overviews and their citations.
- [ ] **MCP Server**: Full support for the **Model Context Protocol**, allowing agents (like Claude or ChatGPT) to use this as a native tool.
- [ ] **CLI JSON Mode**: A flag to print the raw JSON directly to `stdout` for pipe-based consumption by other CLI tools and agents.
- [ ] **Enhanced Code Cleanup**: Ongoing refactor to improve modularity and extraction speed.

---

## 🛡 Handling CAPTCHAs

Google may occasionally present a CAPTCHA. Because we use a persistent browser profile, you can usually solve it once and be set for a long time.

**How to identify/fix:**
1. **Symptoms**: The scraper logs "No more results found" or times out on the first page.
2. **The Fix**: Run the scraper in **headful mode**:
   ```bash
   python scraper.py "your query" --headful
   ```
3. A browser window will open. Solve the CAPTCHA manually.
4. Close the scraper. The session is now saved in `.browser_profile`, and future runs (even in headless mode) will work.

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or have a feature request:
1. **Flag Issues**: Use the [GitHub Issues](https://github.com/sameer920/googleSerpScraper/issues) page. Please include the query used and a screenshot if possible.
2. **Submit PRs**: 
   - Fork the repo.
   - Create a feature branch (`git checkout -b feature/amazing-feature`).
   - Commit your changes (`git commit -m 'Add amazing feature'`).
   - Push to the branch (`git push origin feature/amazing-feature`).
   - Open a Pull Request.

---

## 📜 License

Distributed under the AGPL v3 License. See `LICENSE` for more information.



## ⚖️ Legal Disclaimer

This software is for **educational and research purposes only**. The author does not condone or encourage the scraping of Google Search Result Pages (SERP) in violation of their [Terms of Service](https://policies.google.com/terms).

### 1. No Affiliation
This project is not affiliated with, maintained, authorized, or endorsed by Google LLC or any of its affiliates. "Google" is a registered trademark of Google LLC.

### 2. Use at Your Own Risk
The user is solely responsible for compliance with any third-party terms of service and local, state, or federal laws. The authors and contributors are not responsible for any legal consequences, account bans, or IP blocks resulting from the use of this software.

### 3. No Warranty
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. 

### 4. Indemnification
By using this tool, you agree to indemnify and hold harmless the authors from any and all claims, losses, liabilities, or expenses (including attorney fees) arising out of your use of the software.

---
*Built for the agentic future. Stop paying for search APIs.*
