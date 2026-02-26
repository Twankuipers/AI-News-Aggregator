## Plan: Daily AI News Aggregator with Email Digest

You want an automated system that fetches the latest AI models, papers, and news from multiple sources daily, then sends you an email digest. The agent will use `fetch_webpage` to scrape content and prepare a structured email-ready format. Email delivery will integrate with an external service you'll configure.

**Steps**

1. **Create project structure** in your workspace:
   - `ai_news_agent.py` - Main Python script containing the aggregator logic
   - `agent.md` - Documentation file describing the agent, usage, and architecture
   - `config.json` - Configuration file with news source URLs, filters, and email settings
   - `data/` folder - Store historical fetches and prevent duplicate news items
   - `output/` folder - Generated HTML/text digests ready for email

2. **Build `ai_news_agent.py` core functionality**:
   - `NewsSource` class: Define each source (ArXiv, Hugging Face, GitHub Trending, company blogs) with URL patterns and parsing logic
   - `fetch_arxiv_papers()`: Use `fetch_webpage` to get latest cs.AI and cs.LG papers from ArXiv's recent listings
   - `fetch_huggingface_updates()`: Scrape Hugging Face blog and new model releases
   - `fetch_github_trending()`: Use `github_repo` tool or fetch GitHub trending page for AI/ML repositories
   - `fetch_company_blogs()`: Scrape OpenAI, Anthropic, DeepMind, Google AI blogs for announcements
   - `aggregate_news()`: Combine all sources, deduplicate against `data/seen_items.json`, rank by relevance
   - `generate_email_html()`: Format aggregated news into HTML email template with sections per source
   - `generate_email_text()`: Plain text version for email clients
   - `save_digest()`: Write HTML/text to `output/digest_YYYY-MM-DD.html`

3. **Create `config.json`** with:
   - `sources`: List of URLs and parsing selectors for each news source
   - `keywords`: Filter terms (transformers, LLMs, diffusion models, reinforcement learning, etc.)
   - `email_config`: Placeholder for SMTP settings or API keys (to be filled when external service is set up)
   - `schedule`: "daily" frequency setting
   - `max_items_per_source`: Limit results to avoid overwhelming digest (e.g., 5-10 per source)

4. **Write `agent.md` documentation** including:
   - **Overview**: What the agent does, why it's useful
   - **Architecture**: Diagram/description of data flow (fetch → parse → dedupe → format → email)
   - **News Sources**: List of all sources monitored with example URLs
   - **Usage**: How to run manually (`python ai_news_agent.py`) and schedule (Windows Task Scheduler daily)
   - **Configuration**: Explain `config.json` settings
   - **Email Integration**: Instructions for connecting SendGrid, Gmail SMTP, or Mailgun API
   - **Dependencies**: Required Python packages (`requests`, `beautifulsoup4`, `feedparser`, `html2text`)
   - **Customization**: How to add new sources or modify filters

5. **Implement deduplication system**:
   - Create `data/seen_items.json` to track article URLs/titles already sent
   - Check each fetched item against this history before including in digest
   - Append new items after each run to prevent repeated news

6. **Build email integration hooks**:
   - `EmailSender` class with placeholder methods: `send_via_smtp()`, `send_via_api()`, `send_via_file()`
   - For now, default to `send_via_file()` which saves digest to `output/` for manual sending
   - Document how to uncomment and configure SMTP/API methods when external service is ready

7. **Add scheduling mechanism**:
   - Document Windows Task Scheduler setup in `agent.md` for daily 9 AM execution
   - Include sample PowerShell command: `python C:\Users\twank\Topicus-Local\workshop\ai_news_agent.py`
   - Alternative: Document cron job setup if moving to Linux

8. **Create error handling and logging**:
   - Log file at `logs/agent_YYYY-MM-DD.log` for debugging fetch failures
   - Try-except blocks around each source fetch to prevent one failure from breaking entire run
   - Email notification if agent encounters critical errors (once email is connected)

**Verification**

- **Manual test**: Run `python ai_news_agent.py` and verify `output/digest_YYYY-MM-DD.html` is generated with news from all sources
- **Deduplication test**: Run twice in succession and confirm second run excludes items from first
- **Email preview**: Open generated HTML file in browser to verify formatting looks good
- **Schedule test**: Set up Task Scheduler for next day and confirm it executes automatically
- **Email integration test** (later): Configure SendGrid/Gmail and send yourself a test digest

**Decisions**

- **Chose Python script over Jupyter Notebook**: Better for scheduling and automation, cleaner for production use
- **HTML + text email formats**: HTML for rich formatting, text as fallback for email clients
- **File-based deduplication**: Simple JSON file instead of database since volume is low (daily digest)
- **Modular source architecture**: Easy to add/remove news sources by editing `config.json` without code changes
- **Deferred email integration**: Output to files now, plug in email service when ready without rewriting core logic

---

This plan creates a production-ready AI news aggregator that you can run daily. Once you configure an email service (SendGrid, Gmail SMTP, Mailgun), you'll only need to update `config.json` with credentials and uncomment the email sending code. The agent is designed for easy maintenance and customization.
