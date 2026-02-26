# AI News Aggregator Agent

An automated system that fetches the latest AI models, papers, and news from multiple sources daily and generates an email-ready digest.

## Overview

The AI News Aggregator is a Python-based agent that monitors various AI/ML sources including research papers (ArXiv), model releases (Hugging Face), trending repositories (GitHub), and industry news (company blogs). It aggregates the content, filters by relevance, deduplicates against previous runs, and generates both HTML and plain text digests ready for email distribution.

### Key Features

- 📚 **Multiple Source Support**: ArXiv papers, Hugging Face models, GitHub repos, company blogs
- 🔍 **Smart Filtering**: Keyword-based filtering to focus on relevant topics
- 🚫 **Deduplication**: Tracks previously seen items to avoid sending duplicates
- 📧 **Email-Ready Output**: Generates both HTML and plain text formats
- 🔄 **Scheduled Execution**: Designed for daily automated runs
- 📊 **Comprehensive Logging**: Detailed logs for debugging and monitoring
- ⚙️ **Configurable**: All settings managed via JSON configuration file

## Architecture

### Data Flow

```
┌─────────────────┐
│  News Sources   │
│  - ArXiv        │
│  - Hugging Face │
│  - GitHub       │
│  - Company Blogs│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Fetch Content  │
│ (fetch_webpage) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parse & Extract│
│   News Items    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filter by      │
│   Keywords      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Deduplicate    │
│ (seen_items.json)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Limit Items    │
│   per Source    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate HTML  │
│  & Text Digest  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save to        │
│  output/        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Send Email     │
│  (when enabled) │
└─────────────────┘
```

## Project Structure

```
workshop/
├── ai_news_agent.py      # Main Python script with core logic
├── config.json           # Configuration file
├── agent.md             # This documentation file
├── requirements.txt     # Python dependencies
├── data/
│   └── seen_items.json  # Tracks previously processed items
├── output/
│   ├── digest_YYYY-MM-DD.html  # HTML email digest
│   └── digest_YYYY-MM-DD.txt   # Plain text digest
└── logs/
    └── agent_YYYY-MM-DD.log    # Daily log files
```

## News Sources

The agent monitors the following sources:

### Research Papers
- **ArXiv AI Papers** (`cs.AI`): Latest artificial intelligence research
- **ArXiv ML Papers** (`cs.LG`): Latest machine learning research

### Models & Tools
- **Hugging Face Blog**: New model releases and announcements
- **Hugging Face Trending Models**: Most popular models on the platform

### Open Source
- **GitHub Trending**: Trending Python repositories (filtered for AI/ML)

### Company News
- **OpenAI Blog**: Updates from OpenAI
- **Anthropic News**: Announcements from Anthropic
- **DeepMind Blog**: Research and updates from DeepMind
- **Google AI Blog**: Google's AI developments

## Usage

### Manual Execution

Run the agent manually from the command line:

```bash
python ai_news_agent.py
```

The agent will:
1. Fetch news from all configured sources
2. Filter and deduplicate items
3. Generate digest files in `output/`
4. Log activity to `logs/`

### Scheduled Execution (Windows Task Scheduler)

To run the agent automatically every day:

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create Basic Task**
   - Click "Create Basic Task" in the right panel
   - Name: "AI News Aggregator"
   - Description: "Daily AI news digest generation"

3. **Set Trigger**
   - Frequency: Daily
   - Start time: 9:00 AM (or your preferred time)
   - Recur every: 1 day

4. **Set Action**
   - Action: Start a program
   - Program/script: `python`
   - Add arguments: `ai_news_agent.py`
   - Start in: `C:\Users\twank\Topicus-Local\workshop`

5. **Finish and Test**
   - Right-click the task and select "Run" to test

### Scheduled Execution (Linux/macOS with cron)

Add to your crontab (`crontab -e`):

```bash
0 9 * * * cd /path/to/workshop && python3 ai_news_agent.py
```

## Configuration

Edit `config.json` to customize the agent behavior:

### Sources

Enable or disable specific sources:

```json
{
  "sources": [
    {
      "name": "ArXiv AI Papers",
      "url": "https://arxiv.org/list/cs.AI/recent",
      "category": "Research Papers",
      "enabled": true
    }
  ]
}
```

### Keywords

Filter news items by keywords (case-insensitive):

```json
{
  "keywords": [
    "transformer",
    "LLM",
    "diffusion",
    "reinforcement learning"
  ]
}
```

### Limits

Control the number of items per source:

```json
{
  "max_items_per_source": 10
}
```

### Email Configuration

Configure email delivery (when ready):

```json
{
  "email_config": {
    "enabled": true,
    "method": "smtp",
    "smtp": {
      "host": "smtp.gmail.com",
      "port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password",
      "from_email": "your-email@gmail.com",
      "to_email": "recipient@example.com"
    }
  }
}
```

## Email Integration

The agent is designed to support multiple email delivery methods:

### Option 1: File-Based (Current Default)

Generates HTML and text files in `output/` directory. You can:
- Open the HTML file in a browser and manually send
- Use email client to send the saved files
- Integrate with external automation tools

### Option 2: SMTP (Gmail, Outlook, etc.)

**Gmail Setup:**

1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the generated password
3. Update `config.json`:
   ```json
   {
     "email_config": {
       "enabled": true,
       "method": "smtp",
       "smtp": {
         "host": "smtp.gmail.com",
         "port": 587,
         "username": "your-email@gmail.com",
         "password": "your-app-password",
         "from_email": "your-email@gmail.com",
         "to_email": "recipient@example.com"
       }
     }
   }
   ```

**Outlook Setup:**

```json
{
  "smtp": {
    "host": "smtp-mail.outlook.com",
    "port": 587,
    "username": "your-email@outlook.com",
    "password": "your-password"
  }
}
```

### Option 3: Email API (SendGrid, Mailgun)

**SendGrid Setup:**

1. Sign up at https://sendgrid.com
2. Create an API key
3. Update `config.json`:
   ```json
   {
     "email_config": {
       "enabled": true,
       "method": "api",
       "api": {
         "provider": "sendgrid",
         "api_key": "your-sendgrid-api-key",
         "from_email": "your-verified-sender@example.com",
         "to_email": "recipient@example.com"
       }
     }
   }
   ```

**Mailgun Setup:**

```json
{
  "api": {
    "provider": "mailgun",
    "api_key": "your-mailgun-api-key",
    "domain": "your-domain.mailgun.org"
  }
}
```

## Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

### Required Packages

- `requests`: HTTP library for web requests
- `beautifulsoup4`: HTML parsing
- `lxml`: XML and HTML parser
- `feedparser`: RSS/Atom feed parsing
- `html2text`: Convert HTML to plain text

### Optional Packages (for email)

- `smtplib`: Built-in, for SMTP email sending
- `sendgrid`: For SendGrid API
- `mailgun`: For Mailgun API

## Customization

### Adding New Sources

1. Add source configuration to `config.json`:
   ```json
   {
     "name": "New AI Blog",
     "url": "https://example.com/blog",
     "category": "Company News",
     "enabled": true
   }
   ```

2. Implement fetching logic in `ai_news_agent.py`:
   ```python
   def fetch_new_source(self) -> List[NewsItem]:
       news_items = []
       # Use fetch_webpage tool
       # Parse content
       # Create NewsItem objects
       return news_items
   ```

3. Add to `aggregate_news()` method:
   ```python
   all_news.extend(self.fetch_new_source())
   ```

### Modifying Filters

Edit `config.json` to adjust filtering:

```json
{
  "filters": {
    "exclude_keywords": ["deprecated", "old"],
    "min_description_length": 50,
    "date_range_days": 1
  }
}
```

### Customizing Email Template

Edit the `generate_email_html()` method in `ai_news_agent.py` to change:
- Colors and styling (CSS in `<style>` section)
- Layout and structure
- Section organization
- Footer content

## Troubleshooting

### No Items Found

- Check `logs/agent_YYYY-MM-DD.log` for errors
- Verify internet connectivity
- Check if sources are accessible
- Review keyword filters (might be too restrictive)

### Duplicate Items Appearing

- Verify `data/seen_items.json` exists and is writable
- Check file permissions
- Review deduplication logic in logs

### Email Not Sending

- Verify `email_config.enabled` is `true` in `config.json`
- Check SMTP/API credentials
- Review email service provider's documentation
- Check firewall/antivirus settings
- Look for authentication errors in logs

### Task Scheduler Not Running

- Verify Python is in system PATH
- Check "Start in" directory is correct
- Review Task Scheduler history for error messages
- Ensure user account has proper permissions

## Logging

Logs are stored in `logs/agent_YYYY-MM-DD.log` with:
- Timestamp for each operation
- Source fetch status
- Number of items processed
- Errors and warnings
- Success/failure status

Log levels:
- `INFO`: Normal operation
- `WARNING`: Non-critical issues
- `ERROR`: Failures that need attention

## Security Notes

- Never commit `config.json` with real credentials to version control
- Use environment variables or secure vaults for API keys
- Use app-specific passwords for email accounts
- Regularly rotate API keys and passwords
- Keep `requirements.txt` updated for security patches

## Future Enhancements

Potential improvements:
- Web dashboard for viewing digests
- More granular filtering options
- Support for RSS feeds natively
- Integration with Slack/Discord notifications
- Machine learning-based relevance scoring
- Summarization of long articles
- Multi-language support
- User preference learning

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review configuration in `config.json`
3. Verify all dependencies are installed
4. Test internet connectivity to news sources

## License

This project is provided as-is for personal use.

---

**Last Updated**: February 26, 2026  
**Version**: 1.0.0
